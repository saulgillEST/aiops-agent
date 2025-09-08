from pathlib import Path
from .planner import build_messages, parse_model_json
from .script_workspace import ScriptWorkspace
from .executor import show_script, run_script

def run_session(llm, skill_ctx: str, docs_ctx: str, user_prompts: list, cfg=None, state=None):
    if cfg is None:
        from .config import load_config
        cfg = load_config()
    if state is None:
        from .state_manager import StateManager
        state = StateManager(persistent=cfg.get('session',{}).get('persistent_memory', True))

    ws = ScriptWorkspace(Path(cfg['execution']['working_dir']))
    system_ctx = "You are an AI Ops agent producing safe, idempotent bash."

    pending = list(user_prompts)

    while True:
        user_msg = pending.pop(0) if pending else input("You: ")
        if user_msg.strip().lower() in ("exit","quit"):
            return
        if user_msg.strip().lower() in ("reset","clear"):
            state.clear()
            continue
        state.add_message('user', user_msg)
        messages = build_messages(system_ctx, skill_ctx, docs_ctx, state.state.get('history', []), user_msg)
        raw = llm.chat(messages).get('text','')
        try:
            resp = parse_model_json(raw)
        except Exception:
            print('Failed to parse model response as JSON. Raw response:\n', raw)
            return

        status = resp.get('status')
        if status == 'clarify':
            for q in resp.get('questions', []):
                ans = input(f"{q}\nYour answer: ")
                state.add_message('assistant', q)
                state.add_message('user', ans)
            continue

        if status in ('propose_script','ready_to_run'):
            script = resp.get('script','')
            ws.write_new(script)
            show_script(ws.path)

            mode = cfg['execution'].get('run_mode','ask')
            if mode == 'ask':
                while True:
                    action = input("[explain <line>/change <instr>/approve/run/abort]> ").strip()
                    if action in ("approve","run"):
                        rc, out, err = run_script(ws.path, cfg['execution']['shell'], sandbox=cfg['execution'].get('sandbox'))
                        print(out)
                        if rc == 0:
                            print('✅ Success.')
                        else:
                            print('❌ Failed. Stderr:\n', err)
                        break
                    if action == 'abort':
                        return
                    state.add_message('user', f'Script review action: {action}')
                    break
            elif mode == 'auto':
                print('Auto-run mode: validating and executing...')
                rc, out, err = run_script(ws.path, cfg['execution']['shell'], sandbox=cfg['execution'].get('sandbox'))
                print(out)
                if rc == 0:
                    print('✅ Success (auto).')
                else:
                    print('❌ Failed (auto). Stderr:\n', err)

            nxt = input('Next instruction (or Enter to finish): ').strip()
            if nxt:
                pending.append(nxt)
            else:
                return

        elif status == 'revise_script':
            ws.apply_unified_diff(resp.get('patch',''))
        else:
            notes = resp.get('notes','')
            if notes:
                print(notes)

