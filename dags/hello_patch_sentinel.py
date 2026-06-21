from airflow.sdk import dag, task
import pendulum

@dag(
    dag_id="hello_patch_sentinel",
    start_date=pendulum.datetime(2026, 6, 21, tz="UTC"),
    catchup=False,
    tags=["hello", "patch_sentinel"]
)

def hello_patch_sentinel():
    @task
    def say_hello():
        return "Hello, Patch Sentinel!"
    
    say_hello()


hello_patch_sentinel()