import json
import os.path
import re
import subprocess
import sys
import time

from rich import print as rprint
from rich.console import Console
from rich.table import Table

DEBUG = False
USE_DOCKER_BUILD_CACHE = False


def get_logged_time(output: str, pattern: str):
    return int(re.search(rf"\[JWF\] {pattern}: (\d+)", output).group(1))


def get_value_from_time(output: str, pattern: re.Pattern):
    return re.search(pattern, output, flags=re.RegexFlag.MULTILINE).group(1)


def process_container_output(output: bytearray):
    output = output.decode("utf-8")

    user_time = get_value_from_time(output, r"User time \(seconds\): ([0-9.]+)")
    system_time = get_value_from_time(output, r"System time \(seconds\): ([0-9.]+)")
    cpu_percent = get_value_from_time(output, r"Percent of CPU this job got: (\d+)%")
    time_used = get_value_from_time(
        output, r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): ([0-9ms. ]+)"
    )

    memory_used = re.search(
        r"Maximum resident set size \(kbytes\): ([0-9]+)",
        output,
        flags=re.RegexFlag.MULTILINE,
    ).group(1)

    return (
        user_time,
        system_time,
        cpu_percent,
        time_used,
        int(memory_used),
        round(get_logged_time(output, "STARTING JAVA") / 1_000_000),
        get_logged_time(output, "JAVA STARTED"),
        get_logged_time(output, "FRAMEWORK STARTED"),
        get_logged_time(output, "START FRAMEWORK SHUTDOWN"),
        round(get_logged_time(output, "JAVA STOPPED") / 1_000_000),
    )


def process_dive_output(output: bytearray):
    output = output.decode("utf-8")
    output = output.split("{", maxsplit=1)[1]
    output = "{" + output
    json_data = json.loads(output)
    sizeBytes = json_data["image"]["sizeBytes"]
    efficiencyScore = json_data["image"]["efficiencyScore"]
    return sizeBytes, efficiencyScore


def run_maven(project: str, type: str):
    rprint("Running Maven...")
    work_dir = os.path.join(os.getcwd(), "projects", project)

    docker_image = f"java-web-frameworks/{project}_{type}"

    rprint(
        "----------------------------------------------------------------------------------"
    )
    rprint(f"Building {docker_image}...")
    rprint(f"Work dir: {work_dir}")
    start = time.time_ns()

    command = [
        "docker",
        "build",
        "--file",
        f"../Dockerfile.{type}",
        "--tag",
        docker_image,
    ]

    if not USE_DOCKER_BUILD_CACHE:
        command.append("--no-cache")

    if DEBUG:
        command.extend(["--progress", "plain"])
    else:
        command.append("--quiet")

    command += ["."]

    rprint(f"Command: {command}")
    process = subprocess.Popen(
        command,
        cwd=work_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if DEBUG:
        for c in iter(lambda: process.stdout.read(1), b""):
            sys.stdout.buffer.write(c)
    retval = process.wait()
    if retval != 0:
        raise Exception(f"Error: {retval}")
    end = time.time_ns()
    build_duration = round((end - start) / 1_000_000)
    rprint(f"Docker build returned {retval} in {build_duration}ms")

    rprint(
        "----------------------------------------------------------------------------------"
    )
    rprint(f"Running {docker_image}...")

    command = [
        "docker",
        "run",
        "--interactive",
        "--tty",
        "--rm",
        # "--memory=256m",
        # "--memory-swap=256m",
        # "--cpus=1",
        docker_image,
    ]

    start = time.time_ns()
    process = subprocess.Popen(
        command,
        cwd=work_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = bytearray()
    for c in iter(lambda: process.stdout.read(1), b""):
        if DEBUG:
            sys.stdout.buffer.write(c)
        output += c
    retval = process.wait()
    if retval != 0:
        raise Exception(f"Error: {retval}")

    (
        user_time,
        system_time,
        cpu_percent,
        time_used,
        memory_used,
        starting_java_time,
        java_started_time,
        framework_started_time,
        framework_shutdown_start_time,
        java_stopped_time,
    ) = process_container_output(output)

    end = time.time_ns()
    duration = round((end - start) / 1_000_000)
    rprint(f"Docker run returned {retval} in {duration}ms")

    rprint(
        "----------------------------------------------------------------------------------"
    )

    command = [
        "dive",
        "--json",
        "/dev/stdout",
        docker_image,
    ]

    process = subprocess.Popen(
        command,
        cwd=work_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = bytearray()
    for c in iter(lambda: process.stdout.read(1), b""):
        if DEBUG:
            sys.stdout.buffer.write(c)
        output += c
    retval = process.wait()
    if retval != 0:
        raise Exception(f"Error: {retval}")
    sizeBytes, efficiencyScore = process_dive_output(output)

    rprint(
        "----------------------------------------------------------------------------------"
    )

    return (
        f"{project}_{type}",
        {
            "build_duration": build_duration,
            "user_time": user_time,
            "system_time": system_time,
            "cpu_percent": cpu_percent,
            "time_used": time_used,
            "memory_used": memory_used,
            "starting_java_time": starting_java_time,
            "java_started_time": java_started_time,
            "framework_started_time": framework_started_time,
            "framework_shutdown_start_time": framework_shutdown_start_time,
            "java_stopped_time": java_stopped_time,
            "sizeBytes": sizeBytes,
            "efficiencyScore": efficiencyScore,
        },
    )


def run():
    rprint("Running benchmarks...")

    results = dict()

    res = run_maven("micronaut-maven", "basic")
    results[res[0]] = res[1]

    res = run_maven("micronaut-maven", "native")
    results[res[0]] = res[1]

    res = run_maven("quarkus-maven", "basic")
    results[res[0]] = res[1]

    res = run_maven("quarkus-maven", "native")
    results[res[0]] = res[1]

    res = run_maven("spring-boot-maven", "basic")
    results[res[0]] = res[1]

    res = run_maven("spring-boot-maven", "native")
    results[res[0]] = res[1]

    rprint(
        "----------------------------------------------------------------------------------"
    )
    if DEBUG:
        rprint(f"Results: {results}")

    table = Table(title="Results")

    table.add_column("Project", justify="right")
    table.add_column("Build Duration", justify="right")
    table.add_column("User Time", justify="right")
    table.add_column("System Time", justify="right")
    table.add_column("CPU Percent", justify="right")
    table.add_column("Memory Used", justify="right")
    table.add_column("Java Start Time", justify="right")
    table.add_column("Framework Start Time", justify="right", style="blue")
    table.add_column("Framework Stop Time", justify="right", style="purple")
    table.add_column("Total Time", justify="right")
    table.add_column("Image Size", justify="right")
    table.add_column("Efficiency Score", justify="right")

    for key, value in results.items():
        table.add_row(
            key,
            f"{value["build_duration"]} ms",
            f"{value["user_time"]} s",
            f"{value["system_time"]} s",
            f"{value['cpu_percent']}%",
            f"{round(value['memory_used'] / 1024)} MB",
            f"{value['java_started_time'] - value['starting_java_time']} ms",
            f"{value['framework_started_time'] - value['java_started_time']} ms",
            f"{value['java_stopped_time'] - value['framework_shutdown_start_time']} ms",
            f"{value['java_stopped_time'] - value['starting_java_time']} ms",
            f"{round(value['sizeBytes'] / 1024 / 1024)} MB",
            f"{value['efficiencyScore'] * 100:0.2f}%",
        )

    console = Console()
    console.print(table)
