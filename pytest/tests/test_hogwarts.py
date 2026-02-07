import pytest
from source.hogwarts import Classroom, Student, Teacher, TooManyStudents

# --- FIXTURES (The Setup) ---
@pytest.fixture
def snape():
    return Teacher("Severus Snape")

@pytest.fixture
def harry():
    return Student("Harry Potter")

@pytest.fixture
def ron():
    return Student("Ron Weasley")

@pytest.fixture
def potions_class(snape):
    """Creates an empty Potions class taught by Snape."""
    return Classroom(teacher=snape, students=[], course_title="Potions")

@pytest.fixture
def full_class(snape):
    """Creates a class that is already at capacity (11 students)."""
    # Create 11 dummy students to fill the slots (0 to 10 <= 10 is True)
    students = [Student(f"Student_{i}") for i in range(11)]
    return Classroom(teacher=snape, students=students, course_title="Defense Against the Dark Arts")


# --- TESTS ---

def test_class_creation(potions_class, snape):
    """Test that the fixture set up the class correctly."""
    assert potions_class.course_title == "Potions"
    assert potions_class.teacher.name == "Severus Snape"
    assert len(potions_class.students) == 0

# USING PARAMETRIZE: Test adding multiple different students
@pytest.mark.parametrize("student_name", [
    ("Hermione Granger"),
    ("Draco Malfoy"),
    ("Neville Longbottom")
])
def test_add_students_individually(potions_class, student_name):
    new_student = Student(student_name)
    potions_class.add_student(new_student)
    
    # Check if the last student in the list matches the name we added
    assert potions_class.students[-1].name == student_name
    assert len(potions_class.students) == 1

# USING RAISES: Test the exception limit
def test_class_capacity_limit(full_class):
    """
    The class has 11 students. The logic 'len <= 10' allows adding 
    when len is 10 (resulting in 11).
    Now that len is 11, '11 <= 10' is False, so it should raise Exception.
    """
    new_student = Student("Colin Creevey")
    
    # We expect this specific error to be raised
    with pytest.raises(TooManyStudents):
        full_class.add_student(new_student)

# Test removing a student
def test_remove_student(potions_class, harry):
    potions_class.add_student(harry)
    assert len(potions_class.students) == 1
    
    potions_class.remove_student("Harry Potter")
    assert len(potions_class.students) == 0

# Test changing the teacher
def test_change_teacher(potions_class):
    slughorn = Teacher("Horace Slughorn")
    potions_class.change_teacher(slughorn)
    assert potions_class.teacher.name == "Horace Slughorn"

# USING MARK: Categorizing tests (e.g., 'slow' or 'magic')
# Run specific marks with: pytest -m magic
@pytest.mark.magic
def test_polyjuice_potion_error(potions_class, harry):
    """
    Example of a marked test. 
    Verifies that removing a student who isn't there doesn't crash the code.
    """
    potions_class.add_student(harry)
    # Try to remove someone not in the list
    potions_class.remove_student("Voldemort") 
    
    # Harry should still be there
    assert len(potions_class.students) == 1
    assert potions_class.students[0].name == "Harry Potter"