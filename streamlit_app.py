import asyncio
import inspect
import threading

import streamlit as st

from app.agents.github.github_agent import GitHubAgent
from app.agents.memory import ConversationMemory
from app.router.classifier import QueryClassifier
from app.services.orchestrator import AgentOrchestrator


class AsyncLoopRunner:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self._started = threading.Event()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._started.wait()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self._started.set()
        self.loop.run_forever()

    async def _call(self, func, *args, **kwargs):
        result = func(*args, **kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    def run(self, func, *args, **kwargs):
        if inspect.isawaitable(func):
            future = asyncio.run_coroutine_threadsafe(func, self.loop)
        else:
            future = asyncio.run_coroutine_threadsafe(
                self._call(func, *args, **kwargs),
                self.loop,
            )
        return future.result()

    def close(self):
        if self.loop.is_closed():
            return

        self.loop.call_soon_threadsafe(self.loop.stop)
        self._thread.join()
        self.loop.close()


def get_async_runner():
    runner = st.session_state.get("async_runner")
    if runner is None or not hasattr(runner, "run"):
        runner = AsyncLoopRunner()
        st.session_state.async_runner = runner
    return runner


def get_orchestrator():
    if "orchestrator" not in st.session_state:

        st.session_state.memory = ConversationMemory(max_length=40)
        st.session_state.github_agent = GitHubAgent()
        st.session_state.classifier = QueryClassifier()
        
        with st.spinner("Initializing agents..."):

            runner = get_async_runner()

            runner.run(
                st.session_state.github_agent.initialize
            )

            runner.run(
                st.session_state.classifier.initialize
            )

        st.session_state.orchestrator = AgentOrchestrator(
            classifier=st.session_state.classifier,
            github_agent=st.session_state.github_agent,
            memory=st.session_state.memory,
        )

        st.session_state.chat_history = []
    return st.session_state.orchestrator


def run_async(func, *args, **kwargs):
    runner = get_async_runner()
    return runner.run(func, *args, **kwargs)


def append_message(role: str, content: str):
    st.session_state.chat_history.append({"role": role, "content": content})


def reset_chat():
    for key in [
        "memory",
        "orchestrator",
        "github_agent",
        "classifier",
        "chat_history",
        "async_runner"
    ]:
        if key in st.session_state:
            del st.session_state[key]

    st.rerun()


def main():
    st.set_page_config(page_title="React Agent Chatbot", page_icon="🤖")
    st.title("React Agent Chatbot")
    st.markdown(
        "Use this interface to ask GitHub questions or query the enterprise knowledge base."
    )

    orchestrator = get_orchestrator()

    with st.sidebar:
        st.header("Controls")
        if st.button("Reset conversation"):
            reset_chat()
        st.write("Memory length:", len(st.session_state.memory.get_messages()))
        st.write("Chat turns:", len(st.session_state.chat_history) // 2)

    if st.session_state.chat_history:
        st.markdown("### Recent messages")

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Your message", placeholder="Ask a question...", key="user_input")
        submitted = st.form_submit_button("Send")

    if submitted and user_input:

        # Add user message immediately
        append_message(
            "user",
            user_input
        )

        with st.spinner("Thinking..."):
            try:
                answer = run_async(
                    orchestrator.invoke,
                    user_input
                )
            except Exception as exc:
                st.error(f"Error: {exc}")
                return

        # Add assistant response after completion
        append_message(
            "assistant",
            answer
        )

        st.rerun()


if __name__ == "__main__":
    main()
