from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker


def create_session():
    ses_engine = create_engine('sqlite:///todo.db')
    Session = sessionmaker(bind=ses_engine)
    return Session()


def menu():
  """ Returns menu list """
    menu_list = [
        "Today's tasks",
        "Week's tasks",
        "All tasks",
        "Missed tasks",
        "Add a task",
        "Delete a task",
        "Exit"
    ]
    return menu_list


def delete_task(session):
  """ Display all task and ask user for number of task to delete """
    rows = get_all_tasks(session)
    try:
        index_to_delete = int(input())
        row_to_delete = rows[index_to_delete-1]
    except ValueError as e:
        print(f"ERR: Not a number")
        return
    except IndexError as e:
        print(f"ERR: Wrong number")
        return
    session.delete(row_to_delete)
    session.commit()


def missed_tasks(session):
  """ Displays all missed task in order by the deadline date """
    rows = session.query(Task).filter(Task.deadline < datetime.today().date()).all()
    if rows:
        rows.sort(key=lambda row: row.deadline)
        print_tasks(rows, show_deadline=True)
    else:
        print("All tasks have been completed!")


def add_task(session):
  """ Add a new task to database. 
      Asks user for description and deadline date in format (YYYY-MM-DD)
  """
    print("Enter a task")
    task_description = input()
    print("Enter a deadline")
    try:
        deadline_string = input()
        date_object = datetime.strptime(deadline_string, "%Y-%m-%d")
        new_task = Task(task=task_description, deadline=date_object)
    except ValueError as e:
        print("ERR wrong data\n")
        return
    session.add(new_task)
    session.commit()
    print("The task has been added!\n")


def get_tasks_for(session, for_date):
  """ Returns all tasks for specific deadline """
    return session.query(Task).filter(Task.deadline == for_date).all()


def print_tasks(rows, show_deadline=False):
  """ Display tasks specified in rows """
    if rows:
        for i, row in enumerate(rows):
            line = f"{i + 1}. {row.task}"
            deadline = row.deadline.strftime("%#d %b")
            line = line + f". {deadline}" if show_deadline else line
            print(line)
    else:
        print("Nothing to do!")


def get_todays(session, for_date=datetime.today().date()):
  """ Print all task with today's deadline """
    print(f"Today {for_date.strftime('%d %b')}")
    rows = get_tasks_for(session=session, for_date=for_date)
    print_tasks(rows)


def get_week_tasks(session):
  """ Display tasks for every day for the next seven days """
    for_date = datetime.today()
    for i in range(7):
        rows = get_tasks_for(session=session, for_date=for_date.date())
        print(for_date.strftime("%A %#d %b") + ":")
        print_tasks(rows)
        print()
        for_date += timedelta(days=1)


def get_all_tasks(session):
  """ Returns all the tasks ordered by deadline date """
    rows = session.query(Task).all()
    rows.sort(key=lambda row: row.deadline)
    print_tasks(rows, show_deadline=True)
    return rows


def main():
  """ Main program loop. """
    while True:
        for i, item in enumerate(menu(), start=1):
            num = 0 if (item == "Exit") else i
            print(f"{num}) {item}")

        choice = input()
        print()
        if choice == "0":
            print("Bye!")
            break
        elif choice == "6":
            print("Choose the number of the task you want to delete:")
            delete_task(create_session())
        elif choice == "5":
            add_task(create_session())
        elif choice == "4":
            print("Missed tasks:")
            missed_tasks(create_session())
            print()
        elif choice == "3":
            print("All tasks:")
            get_all_tasks(create_session())
            print()
        elif choice == "2":
            get_week_tasks(create_session())
        elif choice == "1":
            get_todays(create_session())
            print()


if __name__ == "__main__":
  """ Create database with Task table """
    Base = declarative_base()

    class Task(Base):
        __tablename__ = "task"

        id = Column(Integer, primary_key=True)
        task = Column(String, default='User task')
        deadline = Column(Date, default=datetime.today())

        def __repr__(self):
            return f"{self.deadline}: {self.task}"

    engine = create_engine('sqlite:///todo.db')
    Base.metadata.create_all(engine)
   
    main()  # Start the program loop
