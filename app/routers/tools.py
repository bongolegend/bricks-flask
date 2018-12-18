import sys, inspect
# from app.routers.base import BaseRouter
from app import routers


def get_router(router_name=None):
    '''return the router associated with the router_name, or return a dict of routers'''

    all_classes = inspect.getmembers(routers, inspect.isclass)
    
    # only keep those that have Router as parent class
    router_dict = dict()
    for name, cls in all_classes:
        if issubclass(cls, routers.BaseRouter) and cls is not routers.BaseRouter:
            router_dict[name] = cls

    if router_name:
        assert router_name in router_dict, "This router name is not implemented as a router"
        return router_dict[router_name]
    else:
        return router_dict