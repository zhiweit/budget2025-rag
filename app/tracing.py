import phoenix as px
import llama_index.core


def launch_phoenix():
    px.launch_app()
    llama_index.core.set_global_handler("arize_phoenix")


def close_phoenix():
    px.close_app()
