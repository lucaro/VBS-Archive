import json
import os
import sys

def remove_unperformed_tasks(input_file):
    # Load the JSON data from the provided file
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Extract the task IDs from the root level tasks
    performed_task_ids = {task['templateId'] for task in data['tasks']}
    
    # Filter out the tasks from the nested tasks in the template that have not been performed
    data['template']['tasks'] = [task for task in data['template']['tasks'] if task['id'] in performed_task_ids]
    
    # Create the output file name by adding the suffix "_filtered" before the file extension
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_filtered{ext}"
    
    # Save the modified JSON data to the new file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Filtered file saved as {output_file}")

    performedTasks = {(task['name'],task['id']) for task in data['template']['tasks']}
    print("Performed tasks (templateId, Name):")
    for t in performedTasks:
        print(f"{t[1]}\t{t[0]}")

    templateIds = [task['templateId'] for task in data['tasks']]
    missingTemplates = [task['templateId'] for task in data['tasks'] if task['templateId'] not in templateIds]
    if len(missingTemplates) > 0:
        print("MISSING TEMPLATES:")
        print(missingTemplates)

    noSubmissions = [task for task in data['tasks'] if len(task['submissions']) == 0]
    if len(noSubmissions) > 0:
        print("Tasks with no submissions (templateId, taskId):")
        for nst in noSubmissions:
            print(f"{nst['templateId']}\t{nst['taskId']}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python removeUnperformedTasks.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    remove_unperformed_tasks(input_file)
