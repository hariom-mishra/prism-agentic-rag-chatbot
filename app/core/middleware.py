import time
import logging
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("profiler")

class ProfilingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        
        # =========================================================================
        # 1. Simple Datetime & Logger Request Timer (Commented out for learning purpose)
        # =========================================================================
        # start_time = datetime.now()
        # try:
        #     response = await call_next(request)
        # finally:
        #     duration = datetime.now() - start_time
        #     logger.info(f"API Request to {request.method} {request.url.path} took {duration.total_seconds():.6f} seconds to process.")
        # return response

        # =========================================================================
        # 2. cProfile (Commented out for educational/learning purposes)
        # =========================================================================
        # import cProfile
        # import pstats
        # import io
        # 
        # pr = cProfile.Profile()
        # pr.enable()
        # try:
        #     response = await call_next(request)
        # finally:
        #     pr.disable()
        #     s = io.StringIO()
        #     ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        #     ps.print_stats(30) # Top 30 functions
        #     print("\n================== cProfile Start ==================")
        #     print(s.getvalue())
        #     print("================== cProfile End ====================\n")
        # return response

        # =========================================================================
        # 3. line_profiling (Active)
        # =========================================================================
        # Resolve the route handler manually (with recursion for mounted APIRouters)
        from starlette.routing import Match
        
        def find_endpoint(route, scope):
            match, child_scope = route.matches(scope)
            if match == Match.FULL:
                if hasattr(route, "routes"):
                    new_scope = {**scope, **child_scope}
                    for sub_route in route.routes:
                        endpoint = find_endpoint(sub_route, new_scope)
                        if endpoint:
                            return endpoint
                elif hasattr(route, "original_router") and hasattr(route.original_router, "routes"):
                    new_scope = {**scope, **child_scope}
                    for sub_route in route.original_router.routes:
                        endpoint = find_endpoint(sub_route, new_scope)
                        if endpoint:
                            return endpoint
                elif hasattr(route, "endpoint"):
                    return route.endpoint
            return None

        endpoint = None
        for route in request.app.routes:
            endpoint = find_endpoint(route, request.scope)
            if endpoint:
                break
                    
        if endpoint is not None:
            from line_profiler import LineProfiler
            import io
            
            lp = LineProfiler()
            # Register the endpoint function to be profiled line-by-line
            lp.add_function(endpoint)
            
            # Start profiling session
            lp.enable_by_count()
            try:
                response = await call_next(request)
            finally:
                # Stop profiling session
                lp.disable_by_count()
                
                # Write profiling stats to stream and print/log
                stream = io.StringIO()
                lp.print_stats(stream=stream)
                print(f"\n================== line_profiler Start ({request.method} {request.url.path}) ==================")
                print(stream.getvalue())
                print("================== line_profiler End ====================\n")
        else:
            response = await call_next(request)
            
        return response
