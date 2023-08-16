from .database_explorer import ListAct


def plot(database,
         name,
         method,
         i,
         cutoff,
         amount=1,
         location="",
         unit="",
         list_act_input=None,
         strict=False,
         ):
    list_act = ListAct(database, name, method, location, unit, list_act_input)
    list_act.search(strict=strict)
    app = list_act.dashboard(i, method, cutoff, amount)
    app.run_server(port=8058, debug=True, use_reloader=False)


__all__ = ['plot', ]
