from .database_explorer_bw25 import ListAct


def plot(data):
    app = ListAct.dashboard(**data)
    return app
