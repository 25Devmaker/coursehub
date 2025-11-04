"""
Script to add chapters to Java course
"""
from app import app, db, Course, Chapter
import datetime

with app.app_context():
    # Find Java course
    java_course = Course.query.filter_by(title='Java').first()
    
    if not java_course:
        print("Java course not found!")
    else:
        print(f"Found Java course with ID: {java_course.id}")
        
        # Check if chapters already exist
        existing_chapters = Chapter.query.filter_by(course_id=java_course.id).count()
        
        if existing_chapters > 0:
            print(f"Java course already has {existing_chapters} chapters. Skipping...")
        else:
            # Define Java chapters
            java_chapters = [
                {
                    'chapter_number': 1,
                    'title': 'Introduction to Java',
                    'content': '''
                    <h2>What is Java?</h2>
                    <p>Java is a high-level, object-oriented programming language developed by Sun Microsystems (now owned by Oracle). It was released in 1995 and has since become one of the most popular programming languages.</p>
                    
                    <h3>Key Features:</h3>
                    <ul>
                        <li><strong>Platform Independent:</strong> Java code can run on any device with a Java Virtual Machine (JVM)</li>
                        <li><strong>Object-Oriented:</strong> Everything in Java is an object, following OOP principles</li>
                        <li><strong>Simple and Secure:</strong> Java is designed to be easy to learn and use securely</li>
                        <li><strong>Rich API:</strong> Extensive library of classes and methods</li>
                    </ul>
                    
                    <h3>Java Program Structure:</h3>
                    <pre><code>public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}</code></pre>
                    ''',
                    'checkpoint': 'Write a Java program that prints "Welcome to Java Programming"'
                },
                {
                    'chapter_number': 2,
                    'title': 'Data Types and Variables',
                    'content': '''
                    <h2>Java Data Types</h2>
                    <p>Java is a statically-typed language, meaning variables must be declared with a data type before use.</p>
                    
                    <h3>Primitive Data Types:</h3>
                    <ul>
                        <li><strong>byte:</strong> 8-bit integer (-128 to 127)</li>
                        <li><strong>short:</strong> 16-bit integer (-32,768 to 32,767)</li>
                        <li><strong>int:</strong> 32-bit integer</li>
                        <li><strong>long:</strong> 64-bit integer</li>
                        <li><strong>float:</strong> 32-bit floating point</li>
                        <li><strong>double:</strong> 64-bit floating point</li>
                        <li><strong>char:</strong> Single character</li>
                        <li><strong>boolean:</strong> true or false</li>
                    </ul>
                    
                    <h3>Example:</h3>
                    <pre><code>int age = 25;
double price = 99.99;
char grade = 'A';
boolean isActive = true;
String name = "Java";</code></pre>
                    ''',
                    'checkpoint': 'Declare variables for storing your name, age, and GPA'
                },
                {
                    'chapter_number': 3,
                    'title': 'Control Flow Statements',
                    'content': '''
                    <h2>Control Flow in Java</h2>
                    <p>Control flow statements allow you to make decisions and repeat code execution.</p>
                    
                    <h3>If-Else Statement:</h3>
                    <pre><code>int score = 85;
if (score >= 90) {
    System.out.println("Grade: A");
} else if (score >= 80) {
    System.out.println("Grade: B");
} else {
    System.out.println("Grade: C");
}</code></pre>
                    
                    <h3>Switch Statement:</h3>
                    <pre><code>int day = 3;
switch (day) {
    case 1: System.out.println("Monday"); break;
    case 2: System.out.println("Tuesday"); break;
    default: System.out.println("Other day");
}</code></pre>
                    
                    <h3>Loops:</h3>
                    <pre><code>// For loop
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}

// While loop
int count = 0;
while (count < 5) {
    System.out.println(count);
    count++;
}</code></pre>
                    ''',
                    'checkpoint': 'Write a program that prints even numbers from 2 to 20'
                },
                {
                    'chapter_number': 4,
                    'title': 'Arrays and Collections',
                    'content': '''
                    <h2>Arrays in Java</h2>
                    <p>Arrays are used to store multiple values of the same type.</p>
                    
                    <h3>Array Declaration:</h3>
                    <pre><code>// Declaration and initialization
int[] numbers = {1, 2, 3, 4, 5};

// Declaration with size
int[] arr = new int[5];
arr[0] = 10;
arr[1] = 20;</code></pre>
                    
                    <h3>Array Operations:</h3>
                    <pre><code>int[] nums = {1, 2, 3, 4, 5};
System.out.println("Length: " + nums.length);
for (int num : nums) {
    System.out.println(num);
}</code></pre>
                    
                    <h3>ArrayList (Collection):</h3>
                    <pre><code>import java.util.ArrayList;

ArrayList<String> list = new ArrayList<>();
list.add("Java");
list.add("Python");
list.add("C++");
System.out.println(list.get(0));</code></pre>
                    ''',
                    'checkpoint': 'Create an array of 5 integers and find their sum'
                },
                {
                    'chapter_number': 5,
                    'title': 'Methods and Functions',
                    'content': '''
                    <h2>Methods in Java</h2>
                    <p>Methods are blocks of code that perform a specific task. They help in code reusability and organization.</p>
                    
                    <h3>Method Syntax:</h3>
                    <pre><code>// Method declaration
accessModifier returnType methodName(parameters) {
    // method body
    return value;
}</code></pre>
                    
                    <h3>Example:</h3>
                    <pre><code>public class Calculator {
    // Method with parameters and return value
    public int add(int a, int b) {
        return a + b;
    }
    
    // Method without return value
    public void displayMessage(String msg) {
        System.out.println(msg);
    }
    
    // Static method
    public static int multiply(int a, int b) {
        return a * b;
    }
}</code></pre>
                    
                    <h3>Method Overloading:</h3>
                    <pre><code>public int sum(int a, int b) {
    return a + b;
}

public int sum(int a, int b, int c) {
    return a + b + c;
}</code></pre>
                    ''',
                    'checkpoint': 'Create a method that calculates the area of a rectangle'
                },
                {
                    'chapter_number': 6,
                    'title': 'Object-Oriented Programming - Classes and Objects',
                    'content': '''
                    <h2>OOP Concepts in Java</h2>
                    <p>Java is fundamentally object-oriented. Everything in Java revolves around classes and objects.</p>
                    
                    <h3>Class Definition:</h3>
                    <pre><code>public class Student {
    // Attributes/Fields
    private String name;
    private int age;
    
    // Constructor
    public Student(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // Methods
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
}</code></pre>
                    
                    <h3>Creating Objects:</h3>
                    <pre><code>Student student1 = new Student("John", 20);
System.out.println(student1.getName());</code></pre>
                    
                    <h3>Encapsulation:</h3>
                    <p>Using private fields with public getters and setters to control access to data.</p>
                    ''',
                    'checkpoint': 'Create a Book class with title, author, and price attributes'
                },
                {
                    'chapter_number': 7,
                    'title': 'Inheritance',
                    'content': '''
                    <h2>Inheritance in Java</h2>
                    <p>Inheritance allows a class to inherit properties and methods from another class.</p>
                    
                    <h3>Basic Inheritance:</h3>
                    <pre><code>// Parent class
public class Animal {
    protected String name;
    
    public void eat() {
        System.out.println(name + " is eating");
    }
}

// Child class
public class Dog extends Animal {
    public void bark() {
        System.out.println(name + " is barking");
    }
}</code></pre>
                    
                    <h3>Using Inheritance:</h3>
                    <pre><code>Dog myDog = new Dog();
myDog.name = "Buddy";
myDog.eat();  // Inherited method
myDog.bark(); // Own method</code></pre>
                    
                    <h3>super Keyword:</h3>
                    <pre><code>public class Car extends Vehicle {
    public Car() {
        super(); // Calls parent constructor
    }
}</code></pre>
                    ''',
                    'checkpoint': 'Create a Shape class and Rectangle class that extends Shape'
                },
                {
                    'chapter_number': 8,
                    'title': 'Polymorphism',
                    'content': '''
                    <h2>Polymorphism in Java</h2>
                    <p>Polymorphism means "many forms" - the ability to process objects differently based on their type.</p>
                    
                    <h3>Method Overriding:</h3>
                    <pre><code>public class Animal {
    public void makeSound() {
        System.out.println("Animal makes a sound");
    }
}

public class Dog extends Animal {
    @Override
    public void makeSound() {
        System.out.println("Dog barks");
    }
}</code></pre>
                    
                    <h3>Runtime Polymorphism:</h3>
                    <pre><code>Animal animal1 = new Dog();
Animal animal2 = new Cat();
animal1.makeSound(); // Calls Dog's makeSound
animal2.makeSound(); // Calls Cat's makeSound</code></pre>
                    
                    <h3>Abstract Classes:</h3>
                    <pre><code>abstract class Shape {
    abstract void draw();
}

class Circle extends Shape {
    void draw() {
        System.out.println("Drawing Circle");
    }
}</code></pre>
                    ''',
                    'checkpoint': 'Create an abstract Vehicle class and implement it in Car and Bike classes'
                },
                {
                    'chapter_number': 9,
                    'title': 'Exception Handling',
                    'content': '''
                    <h2>Exception Handling in Java</h2>
                    <p>Exceptions are errors that occur during program execution. Java provides try-catch blocks to handle them.</p>
                    
                    <h3>Try-Catch Block:</h3>
                    <pre><code>try {
    int result = 10 / 0;
} catch (ArithmeticException e) {
    System.out.println("Error: " + e.getMessage());
}</code></pre>
                    
                    <h3>Multiple Catch Blocks:</h3>
                    <pre><code>try {
    int[] arr = new int[5];
    arr[10] = 50;
} catch (ArrayIndexOutOfBoundsException e) {
    System.out.println("Array index error");
} catch (Exception e) {
    System.out.println("General error");
}</code></pre>
                    
                    <h3>Finally Block:</h3>
                    <pre><code>try {
    // code
} catch (Exception e) {
    // handle exception
} finally {
    // always executes
    System.out.println("Cleanup code");
}</code></pre>
                    
                    <h3>Throwing Exceptions:</h3>
                    <pre><code>public void checkAge(int age) throws Exception {
    if (age < 18) {
        throw new Exception("Age must be 18 or above");
    }
}</code></pre>
                    ''',
                    'checkpoint': 'Write a program that handles division by zero exception'
                },
                {
                    'chapter_number': 10,
                    'title': 'File Handling and I/O',
                    'content': '''
                    <h2>File I/O in Java</h2>
                    <p>Java provides various classes for reading from and writing to files.</p>
                    
                    <h3>Reading from File:</h3>
                    <pre><code>import java.io.*;

try {
    FileReader file = new FileReader("data.txt");
    BufferedReader reader = new BufferedReader(file);
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
    reader.close();
} catch (IOException e) {
    System.out.println("Error reading file");
}</code></pre>
                    
                    <h3>Writing to File:</h3>
                    <pre><code>try {
    FileWriter writer = new FileWriter("output.txt");
    writer.write("Hello, Java!");
    writer.close();
} catch (IOException e) {
    System.out.println("Error writing file");
}</code></pre>
                    
                    <h3>Using Scanner:</h3>
                    <pre><code>import java.util.Scanner;

Scanner scanner = new Scanner(System.in);
System.out.println("Enter your name:");
String name = scanner.nextLine();
System.out.println("Hello, " + name);
scanner.close();</code></pre>
                    ''',
                    'checkpoint': 'Create a program that reads a text file and counts the number of lines'
                }
            ]
            
            # Add chapters to database
            for chapter_data in java_chapters:
                chapter = Chapter(
                    course_id=java_course.id,
                    chapter_number=chapter_data['chapter_number'],
                    title=chapter_data['title'],
                    content=chapter_data['content'],
                    checkpoint=chapter_data['checkpoint']
                )
                db.session.add(chapter)
            
            db.session.commit()
            print(f"Successfully added {len(java_chapters)} chapters to Java course!")
            print("Chapters added:")
            for ch in java_chapters:
                print(f"  Chapter {ch['chapter_number']}: {ch['title']}")

