import threading
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import schedule
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI

# importing our routers
from app.api import search_router, system_router

# import routers of clustering
from app.api.cluster_routes import router as cluster_router

# importing our services for the scheduled job
from app.services.crawler import run_background_crawler
from app.services.nlp_indexer import do_indexing_and_saving

# defining the scheduled job using our refactored service functions


def scheduled_job():
    print(f"\n{'='*20} running scheduled 90-day crawl at {datetime.now(timezone.utc)} {'='*20}\n")

    # these functions now automatically pull seed_url, user_agent, etc., from your settings
    run_background_crawler()
    do_indexing_and_saving()
    print(f"{20*"="} Crawled, Indexing and Saving completed... {20*"="}")

# wrapping the schedule loop in a function to run in a separate thread


def run_scheduler_blocking():

    # automatically it crawls in every 3 months (tested syccessfully in every 15 mins)
    schedule.every(90).days.do(scheduled_job)

    # continuously checking for pending scheduled jobs
    while True:
        schedule.run_pending()
        time.sleep(60)

# setting up the lifespan context manager to manage background tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # starting the scheduler thread as a daemon so it closes gracefully when the server stops
    scheduler_thread = threading.Thread(
        target=run_scheduler_blocking, daemon=True)
    scheduler_thread.start()
    print("background scheduler thread started successfully.")

    # yielding control back to fastapi to run the actual web server
    yield

    # executing cleanup logic when the server is forcefully shut down
    print("shutting down scheduler thread.")

# initializing the fastapi application with the lifespan manager
app = FastAPI(
    title="Coventry Publications - Vertical Search Engine API",
    description="FastAPI backend for crawling and searching Coventry University research profiles and publications. Developed by Sanjiv Shrestha",
    lifespan=lifespan
)

# adding middleware to use this api in external websites
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# registering the API routers with their respective prefixes
app.include_router(system_router, tags=["System"])
app.include_router(search_router, prefix="/search", tags=["Search"])

# registering the clustering router
app.include_router(cluster_router)
