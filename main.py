import csv
import json
import psycopg2 as ps
import base64 as b64


def initialise_config():
    with open("config.json", "r") as f:
        config = json.loads(f.read())
        config['password'] = b64.b64decode(config['password']).decode()
    return config


def read_from_database(sql_query: str, config: dict):
    try:
        with ps.connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query)
                response = cursor.fetchall()
                columns = [item.name for item in cursor.description]

                new_data = []
                for employee in response:
                    new_data.append(dict(zip(columns, employee)))

                return new_data
    except Exception as e:
        print(f"Failure on reading on database. Error : {e}")


def execute_query(sql_query: str, config: dict):
    try:
        with ps.connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query)
                print("Successfully executed")
                return True

    except Exception as e:
        print(f"Failure on reading on database. Error : {e}")
        return False


if __name__ == '__main__':
    MENU = """
    1. Show all employess
    2. Show all employess by department
    3. Show all projects of a certain employee
    4. Change salary to employee
    5. Hire new employee
    6. Fire employee
    Pick : """

    user_pick = input(MENU)
    config = initialise_config()
    match user_pick:
        case "1":
            emps = read_from_database(sql_query="select * from company.employess", config=config)
            print(json.dumps(emps, indent=4))
        case "2":
            departments = read_from_database(sql_query="select * from company.departments", config=config)
            for department in departments:
                print(f"{department['departament_id']}. {department['departament_name']}")

            department_pick = input("Choose department : ")
            emps = read_from_database(
                sql_query=f"select * from company.employess where department_id = {department_pick}",
                config=config)
            print(json.dumps(emps, indent=4))
        case "3":
            pass
        case "4":
            emps = read_from_database(sql_query="select emp_id, emp_name from company.employess",
                                      config=config)
            for emp in emps:
                print(f"{emp['emp_id']}. {emp['emp_name']}")
            emp_pick = input("Selectati angajatul : ")
            new_salary = input("Care este noul salariu ? ")
            execute_query(f"UPDATE company.employess set salary = {new_salary} where emp_id = {emp_pick}", config)
        case "5":
            pass
        case "6":
            emps = read_from_database(sql_query="select emp_id, emp_name from company.employess order by emp_id",
                                      config=config)
            for emp in emps:
                print(f"{emp['emp_id']}. {emp['emp_name']}")
            emp_pick = input("Selectati angajatul : ")
            consent = input("Are you want to fire this employee? Y/N : ")
            if consent.lower() == "y":
                execute_query(f"DELETE from company.employess where emp_id = {emp_pick}", config)
        case _:
            print("Wrong options !")
