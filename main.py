from bioblend.galaxy import GalaxyInstance
import time

# ========== Configuration ==========
GALAXY_URL = 'https://usegalaxy.org'
API_KEY = 'aeb8e10df85dc9f25a7832e885225338'  # Replace with yours
FILENAME = 'example_file.txt'
HISTORY_NAME = "Bioblend Change Case Demo"

# ========== Connect to Galaxy ==========
gi = GalaxyInstance(url=GALAXY_URL, key=API_KEY)

# ========== Create New History ==========
history = gi.histories.create_history(name=HISTORY_NAME)
print("Created history:", history['id'])

# ========== Upload File ==========
upload = gi.tools.upload_file(FILENAME, history['id'])
upload_output_id = upload['outputs'][0]['id']
print("Uploaded dataset ID:", upload_output_id)

# ========== Wait for Upload to Complete ==========
def wait_for_dataset_ready(dataset_id):
    while True:
        state = gi.datasets.show_dataset(dataset_id)['state']
        print("Waiting for upload... State:", state)
        if state == 'ok':
            break
        elif state == 'error':
            raise Exception("Dataset upload failed.")
        time.sleep(3)

wait_for_dataset_ready(upload_output_id)

# ========== Find 'Change Case' Tool ==========
tools = gi.tools.get_tools(name="Change Case")
if not tools:
    raise Exception("Change Case tool not found in this Galaxy instance.")
tool_id = tools[0]['id']
print("Using tool:", tool_id)

# ========== Run the Tool ==========
inputs = {
    "input": {"src": "hda", "id": upload_output_id},
    "case": "upper"  # can be 'upper' or 'lower'
}
response = gi.tools.run_tool(history['id'], tool_id, tool_inputs=inputs)
job_id = response['jobs'][0]['id']
output_id = response['outputs'][0]['id']
print("Tool job submitted:", job_id)

# ========== Wait for Job to Complete ==========
def wait_for_job_done(job_id):
    while True:
        job_state = gi.jobs.show_job(job_id)['state']
        print("Waiting for tool job... State:", job_state)
        if job_state == 'ok':
            break
        elif job_state == 'error':
            raise Exception("Tool execution failed.")
        time.sleep(5)

wait_for_job_done(job_id)

# ========== Download Output ==========
gi.datasets.download_dataset(
    output_id,
    file_path="converted_output.txt",
    use_default_filename=False
)
print("Downloaded output to: converted_output.txt")
