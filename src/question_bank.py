"""
Question Bank for Interview Preparation
"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Question:
    """Represents an interview question"""
    id: str
    type: str  # technical, behavioral, system_design
    category: str
    difficulty: str
    question: str
    expected_keywords: List[str] = None
    tips: List[str] = None
    
    def __post_init__(self):
        if self.expected_keywords is None:
            self.expected_keywords = []
        if self.tips is None:
            self.tips = []


class QuestionBank:
    """Manages interview questions by category"""
    
    def __init__(self):
        self.questions = self._load_questions()
        self.categories = list(self.questions.keys())
    
    def _load_questions(self) -> Dict[str, List[Question]]:
        """Load all questions into the question bank"""
        return {
            "python": self._get_python_questions(),
            "data_structures": self._get_ds_questions(),
            "algorithms": self._get_algo_questions(),
            "machine_learning": self._get_ml_questions(),
            "system_design": self._get_system_design_questions(),
            "databases": self._get_db_questions(),
            "behavioral": self._get_behavioral_questions(),
        }
    
    def _get_python_questions(self) -> List[Question]:
        return [
            Question(
                id="py_001",
                type="technical",
                category="Python",
                difficulty="easy",
                question="What is the difference between a list and a tuple in Python?",
                expected_keywords=["mutable", "immutable", "parentheses", "bracket"],
                tips=["Mention mutability", "Use cases for each"]
            ),
            Question(
                id="py_002",
                type="technical",
                category="Python",
                difficulty="medium",
                question="Explain Python decorators and provide an example.",
                expected_keywords=["@", "wrapper", "function", "modification"],
                tips=["Show a simple decorator example", "Explain the syntax"]
            ),
            Question(
                id="py_003",
                type="technical",
                category="Python",
                difficulty="medium",
                question="How does Python's garbage collection work?",
                expected_keywords=["reference counting", "garbage collector", "cycles"],
                tips=["Reference counting mechanism", "Generational collection"]
            ),
            Question(
                id="py_004",
                type="technical",
                category="Python",
                difficulty="medium",
                question="What are *args and **kwargs? When would you use them?",
                expected_keywords=["variable arguments", "keyword arguments", "packing"],
                tips=["Show syntax", "Real-world use cases"]
            ),
            Question(
                id="py_005",
                type="technical",
                category="Python",
                difficulty="hard",
                question="Explain the Global Interpreter Lock (GIL) and its impact on multi-threading.",
                expected_keywords=["GIL", "threading", "CPU-bound", "I/O-bound"],
                tips=["What it prevents", "When it's not a problem"]
            ),
            Question(
                id="py_006",
                type="technical",
                category="Python",
                difficulty="medium",
                question="What is the difference between shallow copy and deep copy?",
                expected_keywords=["copy", "reference", "nested", "mutable"],
                tips=["Use copy module", "Nested object behavior"]
            ),
            Question(
                id="py_007",
                type="technical",
                category="Python",
                difficulty="easy",
                question="How do list comprehensions work? Provide an example.",
                expected_keywords=["[ ]", "expression", "iteration", "condition"],
                tips=["Basic syntax", "Compare to loops"]
            ),
            Question(
                id="py_008",
                type="technical",
                category="Python",
                difficulty="medium",
                question="Explain Python's context managers and the 'with' statement.",
                expected_keywords=["__enter__", "__exit__", "resource", "cleanup"],
                tips=["Use try/finally analogy", "Common examples"]
            ),
            Question(
                id="py_009",
                type="technical",
                category="Python",
                difficulty="hard",
                question="What are Python generators? How do they differ from regular functions?",
                expected_keywords=["yield", "lazy evaluation", "iterator", "memory"],
                tips=["Show yield keyword", "Memory efficiency"]
            ),
            Question(
                id="py_010",
                type="technical",
                category="Python",
                difficulty="medium",
                question="Explain the difference between @staticmethod and @classmethod.",
                expected_keywords=["instance", "class", "self", "cls"],
                tips=["When to use each", "Real examples"]
            ),
        ]
    
    def _get_ds_questions(self) -> List[Question]:
        return [
            Question(
                id="ds_001",
                type="technical",
                category="Data Structures",
                difficulty="easy",
                question="What is the time complexity of accessing an element in an array by index?",
                expected_keywords=["O(1)", "constant", "random access"],
                tips=["Big O notation", "Direct memory access"]
            ),
            Question(
                id="ds_002",
                type="technical",
                category="Data Structures",
                difficulty="easy",
                question="Explain the difference between a stack and a queue.",
                expected_keywords=["LIFO", "FIFO", "push", "pop", "enqueue", "dequeue"],
                tips=["Real-world analogies", "Time complexities"]
            ),
            Question(
                id="ds_003",
                type="technical",
                category="Data Structures",
                difficulty="medium",
                question="How would you implement a binary search tree?",
                expected_keywords=["node", "left", "right", "insert", "search"],
                tips=["Class structure", "Core operations"]
            ),
            Question(
                id="ds_004",
                type="technical",
                category="Data Structures",
                difficulty="medium",
                question="What is a hash table and how does it handle collisions?",
                expected_keywords=["hash function", "collision", "chaining", "open addressing"],
                tips=["Collision resolution techniques"]
            ),
            Question(
                id="ds_005",
                type="technical",
                category="Data Structures",
                difficulty="medium",
                question="Explain the difference between BFS and DFS traversal.",
                expected_keywords=["queue", "stack", "level", "depth", "graph"],
                tips=["Data structures used", "Use cases"]
            ),
            Question(
                id="ds_006",
                type="technical",
                category="Data Structures",
                difficulty="medium",
                question="What is a linked list? When would you use it over an array?",
                expected_keywords=["node", "pointer", "dynamic", "O(1) insertion"],
                tips=["Singly vs doubly linked", "Memory layout"]
            ),
            Question(
                id="ds_007",
                type="technical",
                category="Data Structures",
                difficulty="hard",
                question="How does a heap data structure work? What are its common operations?",
                expected_keywords=["heapify", "priority queue", "min-heap", "max-heap"],
                tips=["Tree representation", "Time complexities"]
            ),
            Question(
                id="ds_008",
                type="technical",
                category="Data Structures",
                difficulty="medium",
                question="What is a Trie data structure? What are its applications?",
                expected_keywords=["prefix", "autocomplete", "dictionary", "routing"],
                tips=["String operations", "Space vs time tradeoff"]
            ),
        ]
    
    def _get_algo_questions(self) -> List[Question]:
        return [
            Question(
                id="algo_001",
                type="technical",
                category="Algorithms",
                difficulty="medium",
                question="What is the time complexity of quicksort? When is it worst case?",
                expected_keywords=["O(n log n)", "average", "worst case", "pivot"],
                tips=["Pivot selection impact", "Comparison to mergesort"]
            ),
            Question(
                id="algo_002",
                type="technical",
                category="Algorithms",
                difficulty="hard",
                question="Explain dynamic programming. When would you use it?",
                expected_keywords=["optimal substructure", "overlapping subproblems", "memoization"],
                tips=["Top-down vs bottom-up", "Classic examples"]
            ),
            Question(
                id="algo_003",
                type="technical",
                category="Algorithms",
                difficulty="medium",
                question="How does binary search work? What are its time complexities?",
                expected_keywords=["O(log n)", "sorted array", "mid", "divide and conquer"],
                tips=["Prerequisite", "Iterative vs recursive"]
            ),
            Question(
                id="algo_004",
                type="technical",
                category="Algorithms",
                difficulty="hard",
                question="Explain Dijkstra's algorithm for shortest path finding.",
                expected_keywords=["greedy", "priority queue", "relaxation", "non-negative"],
                tips=["Why greedy works", "Time complexity"]
            ),
            Question(
                id="algo_005",
                type="technical",
                category="Algorithms",
                difficulty="medium",
                question="What is the difference between greedy algorithms and dynamic programming?",
                expected_keywords=["optimal", "local", "global", "choice"],
                tips=["When to use each", "Examples"]
            ),
        ]
    
    def _get_ml_questions(self) -> List[Question]:
        return [
            Question(
                id="ml_001",
                type="technical",
                category="Machine Learning",
                difficulty="easy",
                question="What is the difference between supervised and unsupervised learning?",
                expected_keywords=["labeled", "unlabeled", "classification", "clustering"],
                tips=["Examples of each", "Use cases"]
            ),
            Question(
                id="ml_002",
                type="technical",
                category="Machine Learning",
                difficulty="medium",
                question="Explain overfitting and how to prevent it.",
                expected_keywords=["training data", "validation", "regularization", "cross-validation"],
                tips=["Detection methods", "Solutions"]
            ),
            Question(
                id="ml_003",
                type="technical",
                category="Machine Learning",
                difficulty="medium",
                question="What is the bias-variance tradeoff?",
                expected_keywords=["bias", "variance", "underfitting", "overfitting"],
                tips=["Mathematical formulation", "Practical implications"]
            ),
            Question(
                id="ml_004",
                type="technical",
                category="Machine Learning",
                difficulty="medium",
                question="How does gradient descent work? What are its variants?",
                expected_keywords=["learning rate", "convergence", "SGD", "mini-batch"],
                tips=["Batch vs stochastic", "Learning rate impact"]
            ),
            Question(
                id="ml_005",
                type="technical",
                category="Machine Learning",
                difficulty="hard",
                question="Explain the working of backpropagation in neural networks.",
                expected_keywords=["chain rule", "gradients", "weights", "loss"],
                tips=["Forward pass", "Backward pass"]
            ),
        ]
    
    def _get_system_design_questions(self) -> List[Question]:
        return [
            Question(
                id="sd_001",
                type="system_design",
                category="System Design",
                difficulty="hard",
                question="How would you design a URL shortening service like Bitly?",
                expected_keywords=["hash", "storage", "scaling", "redirection"],
                tips=["Functional requirements", "Non-functional", "Deep dive"]
            ),
            Question(
                id="sd_002",
                type="system_design",
                category="System Design",
                difficulty="hard",
                question="Design a chat application like WhatsApp.",
                expected_keywords=["real-time", "WebSocket", "message queue", "online status"],
                tips=["Architecture", "Scalability", "Security"]
            ),
            Question(
                id="sd_003",
                type="system_design",
                category="System Design",
                difficulty="hard",
                question="How would you design Twitter's newsfeed?",
                expected_keywords=["pull", "push", "fanout", "caching"],
                tips=["Timeline generation", "Ranking"]
            ),
        ]
    
    def _get_db_questions(self) -> List[Question]:
        return [
            Question(
                id="db_001",
                type="technical",
                category="Databases",
                difficulty="easy",
                question="What is the difference between SQL and NoSQL databases?",
                expected_keywords=["relational", "schema", "ACID", "eventual consistency"],
                tips=["Use cases for each", "Tradeoffs"]
            ),
            Question(
                id="db_002",
                type="technical",
                category="Databases",
                difficulty="medium",
                question="Explain ACID properties in database transactions.",
                expected_keywords=["Atomicity", "Consistency", "Isolation", "Durability"],
                tips=["Real-world examples", "Why they matter"]
            ),
            Question(
                id="db_003",
                type="technical",
                category="Databases",
                difficulty="medium",
                question="How does database indexing improve query performance?",
                expected_keywords=["B-tree", "lookup", "scan", "speed"],
                tips=["When to index", "Downsides"]
            ),
            Question(
                id="db_004",
                type="technical",
                category="Databases",
                difficulty="hard",
                question="What is database sharding and when would you use it?",
                expected_keywords=["horizontal", "partition", "distributed", "scale"],
                tips=["Sharding strategies", "Tradeoffs"]
            ),
        ]
    
    def _get_behavioral_questions(self) -> List[Question]:
        return [
            Question(
                id="beh_001",
                type="behavioral",
                category="Leadership",
                difficulty="medium",
                question="Tell me about a time when you led a team through a challenging project.",
                expected_keywords=["challenge", "team", "outcome", "role"],
                tips=["STAR method", "Quantify results"]
            ),
            Question(
                id="beh_002",
                type="behavioral",
                category="Problem Solving",
                difficulty="medium",
                question="Describe a complex problem you solved. What was your approach?",
                expected_keywords=["problem", "solution", "steps", "result"],
                tips=["Break down the process", "Lessons learned"]
            ),
            Question(
                id="beh_003",
                type="behavioral",
                category="Teamwork",
                difficulty="easy",
                question="Tell me about a time you had a conflict with a coworker. How did you handle it?",
                expected_keywords=["conflict", "resolution", "communication", "understanding"],
                tips=["Focus on resolution", "Professional approach"]
            ),
            Question(
                id="beh_004",
                type="behavioral",
                category="Adaptability",
                difficulty="medium",
                question="Describe a situation where you had to adapt quickly to a major change.",
                expected_keywords=["change", "adapt", "flexibility", "outcome"],
                tips=["Show resilience", "Positive attitude"]
            ),
            Question(
                id="beh_005",
                type="behavioral",
                category="Communication",
                difficulty="medium",
                question="Tell me about a time you had to explain a technical concept to a non-technical audience.",
                expected_keywords=["audience", "explanation", "simplification", "understanding"],
                tips=["Analogies", "Visual aids"]
            ),
            Question(
                id="beh_006",
                type="behavioral",
                category="Failure",
                difficulty="hard",
                question="Tell me about a time you failed. What did you learn from it?",
                expected_keywords=["failure", "learning", "improvement", "growth"],
                tips=["Be honest", "Show growth mindset"]
            ),
        ]
    
    def get_random_question(self, category: Optional[str] = None, difficulty: Optional[str] = None) -> Question:
        """Get a random question from the bank"""
        questions = self.questions.get(category.lower() if category else None, [])
        
        if difficulty:
            questions = [q for q in questions if q.difficulty == difficulty.lower()]
        
        if not questions:
            # Flatten all questions
            all_questions = []
            for q_list in self.questions.values():
                all_questions.extend(q_list)
            return random.choice(all_questions)
        
        return random.choice(questions)
    
    def get_questions_by_category(self, category: str) -> List[Question]:
        """Get all questions in a category"""
        return self.questions.get(category.lower(), [])
    
    def get_all_categories(self) -> List[str]:
        """Get all available categories"""
        return self.categories
    
    def generate_interview(self, num_questions: int = 5, mix_types: bool = True) -> List[Question]:
        """Generate a set of random questions for a mock interview"""
        questions = []
        categories = list(self.questions.keys())
        
        if mix_types:
            # Mix technical and behavioral
            tech_cats = [c for c in categories if c != "behavioral"]
            beh_cats = ["behavioral"]
            
            for _ in range(num_questions // 2 + 1):
                if tech_cats:
                    cat = random.choice(tech_cats)
                    questions.append(self.get_random_question(cat))
            
            for _ in range(num_questions - len(questions)):
                questions.append(self.get_random_question("behavioral"))
        else:
            cat = random.choice(categories)
            questions = [self.get_random_question(cat) for _ in range(num_questions)]
        
        random.shuffle(questions)
        return questions[:num_questions]
