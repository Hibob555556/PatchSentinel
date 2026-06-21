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
    def say_hello(number: int):
        return f"Hello, Patch Sentinel! The number is {number}"

    @task
    def increment_number(number: int):
        return number + 1


    @task
    def say_goodbye(number: int):
        return f"Goodbye, Patch Sentinel! The number was {number}."


    starting_number = 42
    hello = say_hello(starting_number)
    new_number = increment_number(starting_number)
    goodbye = say_goodbye(new_number)

    hello >> new_number >> goodbye

hello_patch_sentinel()
