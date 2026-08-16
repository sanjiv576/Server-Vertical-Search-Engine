from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse

# importing our services
from app.services.crawler import run_background_crawler
from app.services.nlp_indexer import do_indexing_and_saving

# for inserting already trained cluster docsgem
from app.services.cluster_engine import (
    setup_initial_clustered_db
)

router = APIRouter()

# wrapping the crawler and indexer into a single executable task


def crawl_and_index_task():
    run_background_crawler()
    do_indexing_and_saving()


@router.get('/')
def home():
    return JSONResponse(status_code=200, content={"message": "Just Chill. Everything is going good..."})


@router.get('/health_status')
def health_status():
    setup_initial_clustered_db()
    # returning a simple 200 ok response to confirm the server is running
    return JSONResponse(status_code=200, content={"message": "Server is live..."})


@router.post('/trigger-crawl')
def trigger_crawl(background_tasks: BackgroundTasks):
    # adding the scraping and indexing job to the fastapi background queue
    background_tasks.add_task(crawl_and_index_task)

    # returning a 202 accepted status indicating the job has started
    return JSONResponse(
        status_code=202,
        content={"message": "Crawling and indexing started in the background."}
    )
