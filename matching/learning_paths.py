"""Learning Path Generator for TalentSphere.

Generates personalized, structured learning roadmaps for candidates based on
their identified missing skills for target jobs.
"""

from .skill_catalog import get_skill_category, get_skill_criticality, normalize_skill

# Knowledge base of curated learning resources, milestones, and projects per skill
CURATED_SKILL_ROADMAPS = {
    "python": {
        "description": "High-level programming language known for readability, backend web development, automation, data science, and AI.",
        "estimated_hours": 30,
        "difficulty": "Beginner-Friendly",
        "resources": [
            {"title": "Official Python Documentation & Tutorial", "url": "https://docs.python.org/3/tutorial/", "type": "Documentation", "free": True},
            {"title": "Python for Everybody (FreeCodeCamp / Coursera)", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "type": "Interactive Course", "free": True},
            {"title": "Corey Schafer Python Programming Tutorial Series", "url": "https://youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU", "type": "Video Course", "free": True},
        ],
        "milestones": [
            {"step": 1, "title": "Syntax & Core Data Types", "details": "Variables, lists, dicts, tuples, flow control (if/for/while), functions."},
            {"step": 2, "title": "Object-Oriented Programming (OOP)", "details": "Classes, inheritance, decorators, exceptions, modules and virtual environments."},
            {"step": 3, "title": "Standard Library & Packages", "details": "Working with JSON, file I/O, requests, pip, and virtual environments."},
        ],
        "project_idea": "Build a Command-Line Task Manager & Web Scraper that parses job listings into JSON/CSV files."
    },
    "django": {
        "description": "The web framework for perfectionists with deadlines. Batteries-included Python framework for scalable backends.",
        "estimated_hours": 35,
        "difficulty": "Intermediate",
        "resources": [
            {"title": "Django Official Getting Started Tutorial", "url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/", "type": "Documentation", "free": True},
            {"title": "MDN Django Web Development Tutorial", "url": "https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django", "type": "Guide", "free": True},
            {"title": "Django REST Framework Official Tutorial", "url": "https://www.django-rest-framework.org/tutorial/quickstart/", "type": "Documentation", "free": True},
        ],
        "milestones": [
            {"step": 1, "title": "MVT Architecture & ORM", "details": "Models, migrations, views, URL routing, and Django admin."},
            {"step": 2, "title": "Authentication & Forms", "details": "User registration, login, session management, CSRF protection, and custom user models."},
            {"step": 3, "title": "APIs & Performance", "details": "Django REST Framework, serializers, caching, database indexing, and query optimization (select_related)."},
        ],
        "project_idea": "Build a RESTful E-Commerce backend API with JWT authentication and Stripe payment integration."
    },
    "react": {
        "description": "A JavaScript library for building component-based user interfaces with reactive state management.",
        "estimated_hours": 30,
        "difficulty": "Intermediate",
        "resources": [
            {"title": "React Official Documentation (react.dev)", "url": "https://react.dev/learn", "type": "Documentation", "free": True},
            {"title": "FreeCodeCamp React Course for Beginners", "url": "https://www.freecodecamp.org/news/free-react-course-for-beginners/", "type": "Interactive Course", "free": True},
            {"title": "Scrimba Learn React", "url": "https://scrimba.com/learn/learnreact", "type": "Interactive Course", "free": True},
        ],
        "milestones": [
            {"step": 1, "title": "JSX & Components", "details": "Functional components, props, state (useState), and event handling."},
            {"step": 2, "title": "Hooks & Lifecycle", "details": "useEffect, custom hooks, useContext, and asynchronous API integration (fetch/axios)."},
            {"step": 3, "title": "State & Router", "details": "React Router DOM v6, Redux Toolkit or Zustand state management, and build optimization."},
        ],
        "project_idea": "Build a real-time Kanban Board dashboard with drag-and-drop cards and dark mode support."
    },
    "javascript": {
        "description": "The universal scripting language of the web, powering frontend interactivity and backend servers (Node.js).",
        "estimated_hours": 25,
        "difficulty": "Beginner-Friendly",
        "resources": [
            {"title": "JavaScript.info — Modern JS Tutorial", "url": "https://javascript.info/", "type": "Guide", "free": True},
            {"title": "MDN Web Docs JavaScript Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript", "type": "Documentation", "free": True},
            {"title": "30 Days of Vanilla JS (Wes Bos)", "url": "https://javascript30.com/", "type": "Video Course", "free": True},
        ],
        "milestones": [
            {"step": 1, "title": "Modern ES6+ Fundamentals", "details": "Let/const, arrow functions, destructuring, spread operators, template literals."},
            {"step": 2, "title": "Asynchronous JavaScript", "details": "Promises, async/await, Fetch API, and Event Loop understanding."},
            {"step": 3, "title": "DOM Manipulation & Events", "details": "Query selectors, event listeners, dynamic DOM rendering, and local storage."},
        ],
        "project_idea": "Build an interactive Weather Dashboard connecting to an external REST API with dynamic chart visualizations."
    },
    "typescript": {
        "description": "Strongly typed programming language that builds on JavaScript, giving you better tooling at any scale.",
        "estimated_hours": 20,
        "difficulty": "Intermediate",
        "resources": [
            {"title": "TypeScript Official Handbook", "url": "https://www.typescriptlang.org/docs/handbook/intro.html", "type": "Documentation", "free": True},
            {"title": "Total TypeScript Fundamentals", "url": "https://www.totaltypescript.com/tutorials", "type": "Interactive Course", "free": True},
        ],
        "milestones": [
            {"step": 1, "title": "Basic Types & Interfaces", "details": "Primitive types, interfaces, type aliases, union & intersection types."},
            {"step": 2, "title": "Generics & Utility Types", "details": "Generic functions/classes, Partial, Omit, Pick, Record utility types."},
            {"step": 3, "title": "Tooling & Integration", "details": "Configuring tsconfig.json, integrating with React/Node, strict mode type safety."},
        ],
        "project_idea": "Convert an existing JavaScript application into fully typed TypeScript with strict compiler options."
    },
    "sql": {
        "description": "Domain-specific language used in programming and designed for managing data held in relational database management systems.",
        "estimated_hours": 20,
        "difficulty": "Beginner-Friendly",
        "resources": [
            {"title": "SQLBolt — Interactive SQL Lessons", "url": "https://sqlbolt.com/", "type": "Interactive Course", "free": True},
            {"title": "Mode Analytics SQL Tutorial", "url": "https://mode.com/sql-tutorial/", "type": "Guide", "free": True},
            {"title": "LeetCode Database SQL Practice", "url": "https://leetcode.com/problemset/database/", "type": "Practice", "free": True},
        ],
        "milestones": [
            {"step": 1, "title": "Basic Queries & Filtering", "details": "SELECT, WHERE, ORDER BY, GROUP BY, HAVING, and aggregate functions (COUNT, SUM, AVG)."},
            {"step": 2, "title": "Joins & Subqueries", "details": "INNER JOIN, LEFT/RIGHT JOIN, subqueries, and table normalization."},
            {"step": 3, "title": "Performance & Indexes", "details": "Creating indexes, analyzing EXPLAIN plans, transactions (ACID), and schema design."},
        ],
        "project_idea": "Design an Analytics Database schema for an Online Retailer and write complex reporting queries with JOINs and aggregations."
    },
    "docker": {
        "description": "Containerization platform to package applications and their dependencies into lightweight containers.",
        "estimated_hours": 15,
        "difficulty": "Intermediate",
        "resources": [
            {"title": "Docker Official Orientation and Web Workshop", "url": "https://docs.docker.com/get-started/", "type": "Documentation", "free": True},
            {"title": "FreeCodeCamp Docker Tutorial for Beginners", "url": "https://www.youtube.com/watch?v=fqMOX6JJhGo", "type": "Video Course", "free": True},
        ],
        "milestones": [
            {"step": 1, "title": "Container Concepts & Commands", "details": "Images vs Containers, docker run, docker ps, port mapping, environment variables."},
            {"step": 2, "title": "Dockerfile & Multi-stage Builds", "details": "Writing efficient Dockerfiles, layer caching, minimizing image sizes."},
            {"step": 3, "title": "Docker Compose", "details": "Orchestrating multi-container web apps (Django + PostgreSQL + Redis)."},
        ],
        "project_idea": "Containerize a Django web app with PostgreSQL database and Redis caching using Docker Compose."
    },
    "kubernetes": {
        "description": "Automated container deployment, scaling, and management platform for cloud-native microservices.",
        "estimated_hours": 30,
        "difficulty": "Advanced",
        "resources": [
            {"title": "Kubernetes Official Basics Tutorial", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "type": "Documentation", "free": True},
            {"title": "Kubernetes Course for Beginners (TechWorld with Nana)", "url": "https://www.youtube.com/watch?v=X48VuDVv0do", "type": "Video Course", "free": True},
        ],
        "milestones": [
            {"step": 1, "title": "Architecture & Core Concepts", "details": "Pods, Deployments, Services, ConfigMaps, and Secrets."},
            {"step": 2, "title": "Networking & Storage", "details": "Ingress controllers, Persistent Volumes (PV), and Persistent Volume Claims (PVC)."},
            {"step": 3, "title": "Scaling & Monitoring", "details": "Horizontal Pod Autoscaler (HPA), health checks (liveness/readiness), and Helm charts."},
        ],
        "project_idea": "Deploy a multi-tier microservice application on a local Minikube Kubernetes cluster with ingress routing."
    },
    "aws": {
        "description": "Amazon Web Services — leading cloud platform offering cloud computing, storage, networking, and serverless infrastructure.",
        "estimated_hours": 30,
        "difficulty": "Intermediate-Advanced",
        "resources": [
            {"title": "AWS Free Tier Training & Fundamentals", "url": "https://aws.amazon.com/getting-started/", "type": "Documentation", "free": True},
            {"title": "AWS Cloud Practitioner Ultimate Course (FreeCodeCamp)", "url": "https://www.youtube.com/watch?v=SOTamWNgDKc", "type": "Video Course", "free": True},
        ],
        "milestones": [
            {"step": 1, "title": "Compute & Storage Core", "details": "EC2 instances, Security Groups, S3 buckets, IAM users and policies."},
            {"step": 2, "title": "Databases & Networking", "details": "RDS (PostgreSQL/MySQL), VPC subnets, Route53, and CloudFront CDN."},
            {"step": 3, "title": "Serverless & Deployment", "details": "AWS Lambda, API Gateway, ECS/Fargate container deployment."},
        ],
        "project_idea": "Deploy an auto-scaling Django web app on AWS Elastic Beanstalk / ECS with RDS PostgreSQL and S3 static media storage."
    },
    "machine learning": {
        "description": "Field of study that gives computers the ability to learn without being explicitly programmed.",
        "estimated_hours": 40,
        "difficulty": "Advanced",
        "resources": [
            {"title": "Coursera Machine Learning Specialization (Andrew Ng)", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "type": "Course", "free": True},
            {"title": "Kaggle Learn — Machine Learning Fundamentals", "url": "https://www.kaggle.com/learn", "type": "Interactive Course", "free": True},
            {"title": "Scikit-Learn Official User Guide", "url": "https://scikit-learn.org/stable/user_guide.html", "type": "Documentation", "free": True},
        ],
        "milestones": [
            {"step": 1, "title": "Data Preprocessing & EDA", "details": "Feature engineering, scaling, missing data imputation using Pandas & Scikit-Learn."},
            {"step": 2, "title": "Supervised & Unsupervised Models", "details": "Linear/Logistic Regression, Decision Trees, Random Forests, K-Means clustering."},
            {"step": 3, "title": "Model Evaluation & Tuning", "details": "Cross-validation, Precision/Recall/F1 metrics, Hyperparameter tuning (GridSearchCV)."},
        ],
        "project_idea": "Build and evaluate a Machine Learning model to predict customer churn or housing prices with Scikit-Learn and deploy API with FastAPI."
    },
}


def get_skill_learning_roadmap(skill_name):
    """Retrieve or generate a structured learning path roadmap for a specific skill."""
    norm = normalize_skill(skill_name)
    category = get_skill_category(norm)
    criticality = get_skill_criticality(norm)

    if norm in CURATED_SKILL_ROADMAPS:
        data = CURATED_SKILL_ROADMAPS[norm].copy()
        data["skill_name"] = norm.title()
        data["category"] = category
        data["criticality"] = criticality
        return data

    # Generic high-quality fallback generator for any unrecognized tech skill
    title_name = skill_name.strip().title()
    return {
        "skill_name": title_name,
        "category": category,
        "criticality": criticality,
        "description": f"Master {title_name} to strengthen your {category} capabilities and match modern engineering requirements.",
        "estimated_hours": 20,
        "difficulty": "Intermediate",
        "resources": [
            {
                "title": f"Official {title_name} Documentation & Guides",
                "url": f"https://www.google.com/search?q={title_name}+official+documentation",
                "type": "Documentation",
                "free": True,
            },
            {
                "title": f"FreeCodeCamp & YouTube Tutorials for {title_name}",
                "url": f"https://www.youtube.com/results?search_query=learn+{title_name}+tutorial",
                "type": "Video Course",
                "free": True,
            },
        ],
        "milestones": [
            {"step": 1, "title": "Core Fundamentals", "details": f"Learn key syntax, foundational patterns, and environment setup for {title_name}."},
            {"step": 2, "title": "Practical Application", "details": f"Build basic sample scripts and integrate {title_name} into existing project modules."},
            {"step": 3, "title": "Advanced Mastery", "details": f"Study performance best practices, testing strategies, and production readiness for {title_name}."},
        ],
        "project_idea": f"Build a practical demo application featuring {title_name} and document it in your GitHub portfolio.",
    }


def generate_learning_path(missing_skills, target_job_title="Target Position"):
    """
    Generate a complete personalized learning path plan for a candidate's
    missing skills for a specific job posting.
    """
    roadmaps = []
    total_estimated_hours = 0

    for skill in missing_skills:
        roadmap = get_skill_learning_roadmap(skill)
        roadmaps.append(roadmap)
        total_estimated_hours += roadmap.get("estimated_hours", 20)

    # Sort roadmaps: Critical Core skills first, then by estimated hours
    roadmaps.sort(key=lambda r: (0 if r["criticality"] == "Critical Core" else 1, -r.get("estimated_hours", 0)))

    # Estimate study duration in weeks assuming 10 hours/week study commitment
    weeks_estimate = max(1, round(total_estimated_hours / 10.0))

    return {
        "target_job_title": target_job_title,
        "missing_skill_count": len(missing_skills),
        "total_estimated_hours": total_estimated_hours,
        "estimated_completion_weeks": weeks_estimate,
        "roadmaps": roadmaps,
    }
