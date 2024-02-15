from clearml import PipelineController


def main():
    pipe = PipelineController(
        name="Pipeline Controller BEDU",
        project="examples",
        version="0.0.0",
        auto_version_bump=True,
        # abort_on_failure = True,
        # repo = 'https://github.com/Zarach/NeuroExplicitProblog.git'
    )

    pipe.add_function_step(
        name="increment_step_1",
        function=increment,
        function_return=["incremented_number"],
        cache_executed_step=True,
    )

    pipe.add_function_step(
        name="increment_step_2",
        parents=["increment_step_1"],
        function=increment,
        function_kwargs=dict(i="${increment_step_1.incremented_number}"),
        function_return=["incremented_number"],
        cache_executed_step=True,
    )
    pipe.set_default_execution_queue("default")
    pipe.start(queue="default")


def increment(i: int = 0, limit: int = 2) -> int:
    if i < limit:
        print(f"incrementing from {i} of {i+1}")
        return i + 1
    else:
        print("limit reached")
        return i


if __name__ == "__main__":
    main()