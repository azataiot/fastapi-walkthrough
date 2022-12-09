def get_full_name(first_name: str, last_name: str) -> str:
    full_name = first_name.title() + ' ' + last_name.title()
    return full_name


print(get_full_name("john", "doe"))


class Person:
    def __init__(self, name: str):
        self.name = name


def get_person_name(one_person: Person) -> str:
    return one_person.name


p1 = Person(name="Trump")

print(get_person_name(p1))
