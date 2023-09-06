from .database_explorer import ListAct


def plot(database,
         list_act_input,
         methods,
         cutoff,
         amount=1,
         unit="",
         ):
    list_act = ListAct(database, list_act_input, methods)
    list_act.get_lists()
    list_act.print_lists()
    app = list_act.dashboard(methods, cutoff, unit, amount)
    app.run_server(port=8058, debug=True, use_reloader=False)


__all__ = ['plot', ]
