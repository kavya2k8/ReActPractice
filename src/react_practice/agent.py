import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

students = [
    {
        "student_id": "S001",
        "name": "Kavya V",
        "email": "kavya@example.com",
        "course": "Agentic AI",
        "instructor": "Dr. Smith",
        "completed_assignments": 3,
        "pending_assignments": 1,
        "overdue_assignments": 0
    },
    {
        "student_id": "S002",
        "name": "John Carter",
        "email": "john@example.com",
        "course": "Python",
        "instructor": "Dr. Brown",
        "completed_assignments": 4,
        "pending_assignments": 0,
        "overdue_assignments": 1
    },
    {
        "student_id": "S003",
        "name": "Priya Shah",
        "email": "priya@example.com",
        "course": "Machine Learning",
        "instructor": "Dr. Adams",
        "completed_assignments": 5,
        "pending_assignments": 2,
        "overdue_assignments": 0
    },
    {
        "student_id": "S004",
        "name": "Michael Lee",
        "email": "michael@example.com",
        "course": "Data Science",
        "instructor": "Dr. Wilson",
        "completed_assignments": 2,
        "pending_assignments": 2,
        "overdue_assignments": 2
    },
    {
        "student_id": "S005",
        "name": "Sara Williams",
        "email": "sara@example.com",
        "course": "Generative AI",
        "instructor": "Dr. Taylor",
        "completed_assignments": 6,
        "pending_assignments": 0,
        "overdue_assignments": 0
    }
]

print("Student Data:")
for student in students:
    print(json.dumps(student, indent=4))

def get_student_by_id(student_name: str):
    for student in students:
        if student["name"].lower() == student_name.lower():
            return json.dumps(student, indent=4)
    return json.dumps({
        "status": "error",
        "message": f"Student '{student_name}' was not found"
    })

print("\nFetching student by name 'Kavya V':")
print(get_student_by_id("Kavya V"))

def check_pending_overdue_assignments(student_name: str):
    student_data = get_student_by_id(student_name)
    student = json.loads(student_data)
    
    if "status" in student and student["status"] == "error":
            return json.dumps({
        "status": "error",
        "message": f"Student '{student_name}' was not found"
    })
    
    pending = student["pending_assignments"]
    overdue = student["overdue_assignments"]
    
    messages = []

    if pending > 0:
        messages.append(f"{pending} pending assignments")

    if overdue > 0:
        messages.append(f"{overdue} overdue assignments")

    if messages:
        return json.dumps({
            "status": "warning",
            "message": f"Student '{student_name}' has " + " and ".join(messages) + "."
        })

    return json.dumps({
        "status": "success",
        "message": f"Student '{student_name}' has no pending or overdue assignments."
    })

def check_completed_assignments(student_name: str):
    student_data = get_student_by_id(student_name)
    student = json.loads(student_data)
    
    if "status" in student and student["status"] == "error":
        return json.dumps({
            "status": "error",
            "message": f"Student '{student_name}' was not found"
        })
    
    completed = student["completed_assignments"]
    
    return json.dumps({
        "status": "success",
        "message": f"Student '{student_name}' has completed {completed} assignments."
    })

AVAILABLE_FUNCTIONS = {
    "get_student_profile": get_student_by_id,
    "check_pending_overdue_assignments": check_pending_overdue_assignments,
    "check_completed_assignments": check_completed_assignments,
}

tools_schema  =[
    {
       "type": "function",
       "function": {
        "name": "get_student_profile",
        "description": "Get the profile of a student by their name",
        "parameters": {
            "type": "object",
            "properties": {
                "student_name": {
                    "type": "string"
                }
            },
            "required": ["student_name"]
        }
    }
    },
    {
       "type": "function",
       "function": {
        "name": "check_pending_overdue_assignments",
        "description": "Check for pending and overdue assignments for a student",
        "parameters": {
            "type": "object",
            "properties": {
                "student_name": {
                    "type": "string"
                }
            },
            "required": ["student_name"]
        }
       }
    },
    {
       "type": "function",
       "function": {
        "name": "check_completed_assignments",
        "description": "Check the number of completed assignments for a student",
        "parameters": {
            "type": "object",
            "properties": {
                "student_name": {
                    "type": "string"
                }
            },
            "required": ["student_name"]
        }
    }
    }
]

def run_agent(prompt: str):
    messages=[
                {"role": "system", "content":"You are a helpful assistant that can provide information about students"},
                {"role": "user", "content": prompt}
            ]
    while True:
       response = client.chat.completions.create(
             model="gpt-4o-mini",
         messages=messages,
         tools=tools_schema,
         tool_choice="auto"
         )
       
       response_msg = response.choices[0].message
       messages.append(response_msg)
       if response_msg.tool_calls:
           for tool_call in response_msg.tool_calls:
                tool_name= tool_call.function.name
                tool_args= json.loads(tool_call.function.arguments)
                function_to_call = AVAILABLE_FUNCTIONS.get(tool_name)
                if function_to_call:
                    tool_response = function_to_call(**tool_args)
                    messages.append({"role": "tool", "name": tool_name, "content": tool_response,  "tool_call_id": tool_call.id,})

       else:
            print(f"\n[FINAL RESPONSE]: {response_msg.content}")
            break

run_agent("Get the profile of student 'Kavya V' and check for pending and overdue assignments.")