#!/usr/bin/env bash
set -euo pipefail

cd /workspace/awesome-reviewers

# Idempotency guard
if grep -qF "AI is transforming how developers work. A large majority of developers are using" "_skills/ai-assisted-development/SKILL.md" && grep -qF "Writing **clean code** is a superpower for long-term productivity. Developers sh" "_skills/code-readability/SKILL.md" && grep -qF "Great developers continually refactor code to make it simpler and more efficient" "_skills/code-refactoring/SKILL.md" && grep -qF "Software is increasingly data-driven, and developers who can handle data and ML " "_skills/data-ml/SKILL.md" && grep -qF "DevOps and cloud skills combine software development with IT operations. Modern " "_skills/devops-cloud/SKILL.md" && grep -qF "Effective developers write code and documentation. This includes inline comments" "_skills/documentation/SKILL.md" && grep -qF "Full-stack developers can build end-to-end applications, handling both the clien" "_skills/full-stack-development/SKILL.md" && grep -qF "In the age of constant cyber threats, security is everyone\u2019s job. Developers are" "_skills/secure-coding/SKILL.md" && grep -qF "Building software is usually a team effort. Strong collaboration skills \u2013 commun" "_skills/team-collaboration/SKILL.md" && grep -qF "Writing robust software requires verifying that it works as intended. Developers" "_skills/testing-debugging/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/_skills/ai-assisted-development/SKILL.md b/_skills/ai-assisted-development/SKILL.md
@@ -0,0 +1,17 @@
+---
+name: ai-assisted-development
+description: Leveraging AI coding assistants and tools to boost development productivity, while maintaining oversight to ensure quality results.
+version: '1.0'
+---
+# AI-Assisted Development
+
+AI is transforming how developers work. A large majority of developers are using or planning to use AI tools in their development process. Tools like GitHub Copilot and ChatGPT can generate code, write tests, and even help debug. The ability to effectively use these assistants is a new superpower – it can dramatically speed up routine tasks. However, developers must also critically review AI output because many still do not fully trust AI accuracy and see it struggle with complex tasks.
+
+## Examples
+- Using an AI pair programmer to generate a boilerplate module, then refining and optimizing that code manually.
+- Asking an AI tool to explain a piece of code or suggest fixes for a bug, speeding up the debugging process while double-checking its suggestions.
+
+## Guidelines
+- **Embrace AI Tools:** Integrate AI assistants into your workflow for tasks like code generation, documentation drafting, and test case suggestions. These tools can significantly boost productivity for routine coding tasks.
+- **Validate AI Output:** Always review and test code produced by AI. Treat AI suggestions as helpful drafts, not final solutions. It’s a critical skill to critique and improve AI-generated code – add missing error handling, fix inefficient logic, and ensure it fits your project’s style and requirements.
+- **Stay in Control:** Use AI to augment your work, not replace your thinking. Be aware of known limitations (AI might produce insecure or incorrect code). Maintain rigorous quality practices (code reviews, tests) for AI-written code just as you would for human-written code to ensure reliability.
diff --git a/_skills/code-readability/SKILL.md b/_skills/code-readability/SKILL.md
@@ -0,0 +1,17 @@
+---
+name: code-readability
+description: Writing clean, understandable, and self-documenting code that is easy to review and maintain over time.
+version: '1.0'
+---
+# Code Readability & Maintainability
+
+Writing **clean code** is a superpower for long-term productivity. Developers should prioritize clarity and explicitness over clever brevity. Code that clearly communicates its intent is easier for teammates (and future you) to understand and modify. High readability also reduces the chance of bugs – clear, well-structured code is more maintainable and less prone to surprise behaviors.
+
+## Examples
+- Using meaningful variable and function names (`isServerConnected` instead of `enabled`) to convey intent.
+- Replacing a cryptic one-liner with a few well-named intermediate variables that make the logic obvious.
+
+## Guidelines
+- **Descriptive Naming:** Choose specific, descriptive names for variables, functions, and classes. Names should communicate intent and avoid ambiguity. For example, prefer `getUserProfile()` over `getData()` to make the code self-explanatory.
+- **Clarity Over Cleverness:** Opt for explicit and straightforward code constructs rather than implicit or overly clever ones. For instance, use clear type conversions and named constants instead of magic numbers or implicit casts. This improves readability and avoids confusion.
+- **Maintainability:** Keep code structure simple and organized. Write code in a way that reduces cognitive load on the reader – e.g. clear logic flow and consistent style. Clean, readable code is easier to debug and prevents subtle bugs that can arise from unclear operations.
diff --git a/_skills/code-refactoring/SKILL.md b/_skills/code-refactoring/SKILL.md
@@ -0,0 +1,17 @@
+---
+name: code-refactoring
+description: The practice of restructuring and simplifying code continuously – reducing complexity, improving design, and keeping codebases clean.
+version: '1.0'
+---
+# Code Refactoring & Simplicity
+
+Great developers continually refactor code to make it simpler and more efficient. Over time, software accumulates complexity; refactoring is the skill of untangling that complexity. By breaking down large functions and eliminating unnecessary logic, you improve readability and reduce technical debt. Simple designs are easier to test and evolve.
+
+## Examples
+- Splitting a 300-line function that does many things into smaller helper functions each focused on one task.
+- Removing duplicate code by refactoring it into a reusable module or library.
+
+## Guidelines
+- **Decompose Large Functions:** If a function is doing too much or exceeds roughly 50 lines, split it into smaller, focused functions. Each function should ideally handle one responsibility. This makes the code easier to understand and test.
+- **Simplify Complex Logic:** Reduce nesting and complexity in control flow. Apply the “exit early” principle to handle edge cases upfront and avoid deep nested `if`/`else` blocks. For example, return early on error conditions instead of wrapping the main logic in an else-clause.
+- **Eliminate Redundancy:** Refactor to remove duplicate or convoluted code. Break down complex boolean expressions or chained operations into simpler steps. Simplifying tricky code by using clearer constructs or standard library functions makes it more approachable and reduces potential bugs.
diff --git a/_skills/data-ml/SKILL.md b/_skills/data-ml/SKILL.md
@@ -0,0 +1,17 @@
+---
+name: data-ml
+description: Competence in data analytics and machine learning, enabling developers to build data-driven features and integrate AI/ML capabilities.
+version: '1.0'
+---
+# Data & Machine Learning Proficiency
+
+Software is increasingly data-driven, and developers who can handle data and ML have a strong advantage. Python’s ongoing popularity is largely due to its use in data science and machine learning. Being able to analyze datasets, use ML libraries, and incorporate AI models into applications is a sought-after skill. Whether it’s integrating an ML API or building a model in-house, understanding how these technologies work is crucial in 2025.
+
+## Examples
+- Using Python libraries like **Pandas** and **NumPy** to manipulate and analyze data for an application feature.
+- Integrating a pre-trained machine learning model (e.g. image recognition, NLP) into a web service or app.
+
+## Guidelines
+- **Learn Data Tools:** Gain proficiency with data-focused languages and libraries. For example, Python paired with libraries such as NumPy and Pandas is extremely popular for data tasks. This enables you to perform analysis or preprocessing as part of your development work.
+- **Understand ML Workflows:** Even if you’re not a data scientist, understand the basics of training and using machine learning models. Know how to use ML frameworks or services (TensorFlow, PyTorch, scikit-learn, or cloud ML APIs) to add AI capabilities to applications.
+- **Data-Driven Decision Making:** Use data to inform development decisions. This could mean instrumenting your app with analytics (and then querying that data), or A/B testing features. A developer who can derive insights from data and adjust software accordingly will create more effective, user-optimized products.
diff --git a/_skills/devops-cloud/SKILL.md b/_skills/devops-cloud/SKILL.md
@@ -0,0 +1,17 @@
+---
+name: devops-cloud
+description: Skill in automating software deployment pipelines and managing cloud infrastructure for scalable, reliable systems.
+version: '1.0'
+---
+# DevOps & Cloud Infrastructure
+
+DevOps and cloud skills combine software development with IT operations. Modern developers are expected to deploy and run their code in the cloud, using platforms like AWS, Azure, or GCP. In 2024, AWS was the dominant cloud platform (used by 53% of developers). Competence in cloud-native architecture and CI/CD automation ensures that software can scale and remain stable in production.
+
+## Examples
+- Setting up a CI/CD pipeline that builds, tests, and deploys an application to AWS or Azure.
+- Containerizing a web service with Docker and orchestrating it with Kubernetes for scalable deployment.
+
+## Guidelines
+- **Cloud Platform Proficiency:** Learn to deploy and manage applications on cloud services (AWS, Azure, GCP). AWS remains hugely popular, used by over half of developers, due to its broad ecosystem. Knowing how to configure servers, storage, and networks in a cloud environment is key.
+- **CI/CD Automation:** Embrace continuous integration and deployment. Automate build, test, and deployment workflows using tools like GitHub Actions, Jenkins, or GitLab CI. Containerization (e.g. Docker) is widely used in CI/CD pipelines to ensure consistent deployments across environments.
+- **Infrastructure as Code:** Manage infrastructure with code (Terraform, CloudFormation) and configuration management. Treat operations tasks (provisioning servers, setting up load balancers, monitoring) as part of the development process to enable rapid, reliable releases.
diff --git a/_skills/documentation/SKILL.md b/_skills/documentation/SKILL.md
@@ -0,0 +1,17 @@
+---
+name: documentation
+description: Communicating the intended behavior and context of code through clear documentation and comments, and sharing knowledge with the team.
+version: '1.0'
+---
+# Documentation & Knowledge Sharing
+
+Effective developers write code and documentation. This includes inline comments explaining non-obvious code and higher-level docs that describe modules and systems. Good documentation ensures that knowledge is shared, onboarding is easier, and future maintainers understand the rationale behind decisions. In 2025’s collaborative environments, this skill is invaluable for team velocity.
+
+## Examples
+- Writing a README for a project that explains how to set it up and the overall architecture.
+- Adding a comment in code to clarify why a workaround is used, or marking a section as deprecated with explanation.
+
+## Guidelines
+- **Comment for Clarity:** Add explanatory comments where code isn’t self-explanatory – for example, to clarify complex algorithms, workarounds, or important decisions. A brief comment can save others (and your future self) lots of time understanding the code’s intent.
+- **Keep Docs Up-to-Date:** Treat documentation as a living part of the code. Whenever code behavior changes, update relevant comments and docs accordingly. This prevents misleading information. Inline code comments should always reflect the current state of the code.
+- **Project Documentation:** Adhere to your project’s documentation standards for things like API docs, developer guides, or maintainers lists. For instance, if contributing to an open-source project, ensure files like `OWNERS` are updated properly to reflect component maintainers. Proper docs ensure transparency and smooth knowledge transfer.
diff --git a/_skills/full-stack-development/SKILL.md b/_skills/full-stack-development/SKILL.md
@@ -0,0 +1,17 @@
+---
+name: full-stack-development
+description: Ability to develop both front-end and back-end systems, integrating user interfaces with server logic and databases.
+version: '1.0'
+---
+# Full-Stack Development
+
+Full-stack developers can build end-to-end applications, handling both the client-side and server-side. This is the most common developer role – about one in three developers identifies as full-stack. Mastery of front-end technologies (HTML, CSS, JavaScript/TypeScript) and back-end technologies (server frameworks, databases) allows for building complete features independently. Modern tooling (e.g. Node.js) even enables using one language across the stack, improving efficiency.
+
+## Examples
+- Creating a web application with a React (front-end) and Node.js/Express (back-end) stack.
+- Designing an API server and the accompanying front-end interface that consumes it.
+
+## Guidelines
+- **Front & Back Proficiency:** Build competency in both front-end (e.g. React or other JS frameworks) and back-end (e.g. Node.js, Python, Java) development. Most developers today are expected to span both areas in a **full-stack** capacity.
+- **Unified Tech Stack:** Leverage technologies that allow sharing code or language between client and server. For example, using Node.js for server-side enables using JavaScript/TypeScript in both front-end and back-end, allowing real-time, scalable applications with a single language.
+- **Integrate Databases & APIs:** Be comfortable designing database schemas and building RESTful or GraphQL APIs. Full-stack work often involves linking the UI to persistent storage and external services, requiring knowledge of SQL/NoSQL databases and API design best practices.
diff --git a/_skills/secure-coding/SKILL.md b/_skills/secure-coding/SKILL.md
@@ -0,0 +1,17 @@
+---
+name: secure-coding
+description: Incorporating security at every step of software development – writing code that defends against vulnerabilities and protects user data.
+version: '1.0'
+---
+# Secure Coding Practices
+
+In the age of constant cyber threats, security is everyone’s job. Developers are on the front lines of safeguarding applications, from locking down APIs to securing cloud deployments. This skill means anticipating how code could be exploited and coding defensively. With a majority of organizations attributing breaches to lack of cyber skills, there’s high demand for developers who can build secure systems from the ground up.
+
+## Examples
+- Validating all inputs and encoding outputs to prevent injection attacks (SQL injection, XSS, etc.).
+- Using secure libraries and protocols (HTTPS, OAuth) and storing sensitive data (passwords, API keys) in encrypted form or secret managers.
+
+## Guidelines
+- **Follow Security Best Practices:** Adhere to well-known secure coding standards like the OWASP Top 10. Validate inputs, use proper authentication and error handling, and keep dependencies up to date to patch known vulnerabilities. These habits prevent common exploits.
+- **DevSecOps Mindset:** Integrate security checks into development. Perform code reviews and use automated tools (scanners, dependency checks) to catch flaws early. For example, run static analysis to detect insecure code patterns before they reach production.
+- **Cloud & API Security:** Be aware of security for the platforms you use. Protect cloud infrastructure with appropriate configurations and services and secure your APIs with authentication, authorization, and rate-limiting. Understanding cloud security is now essential for developers, not just dedicated security teams.
diff --git a/_skills/team-collaboration/SKILL.md b/_skills/team-collaboration/SKILL.md
@@ -0,0 +1,17 @@
+---
+name: team-collaboration
+description: Working effectively with others in coding projects – including code reviews, clear communication, and contributing to shared or open-source codebases.
+version: '1.0'
+---
+# Collaboration & Open Source Contribution
+
+Building software is usually a team effort. Strong collaboration skills – communicating with team members, reviewing each other’s code, and following shared conventions – are essential. Many developers also participate in open-source projects to share knowledge and improve their skills. Contributing to open source is recommended for new developers to gain experience and visibility. Ultimately, being able to work well with others (often asynchronously, across different time zones or via platforms like GitHub) is a key developer superpower.
+
+## Examples
+- Participating in code review: reviewing a colleague’s pull request and providing constructive feedback, as well as responding to feedback on your own code.
+- Contributing a bug fix or new feature to an open-source project, following the project’s contribution guidelines and coding style.
+
+## Guidelines
+- **Code Review Mastery:** Engage in code reviews regularly. Read others’ code and provide helpful suggestions, and incorporate feedback from reviewers on your code. For example, if reviewers suggest a function be split for clarity, be willing to refactor. Code review culture leads to better code quality and knowledge transfer.
+- **Open Source Engagement:** Consider contributing to open-source projects or internal company repositories. This exposes you to large-scale codebases and different perspectives. It’s also a great way to demonstrate skills. Always follow the project’s contribution guidelines when submitting changes.
+- **Team Communication:** Maintain clear and professional communication with team members. Document decisions, update project artifacts, and respect established team conventions. By aligning with team processes, you build trust and velocity in development.
diff --git a/_skills/testing-debugging/SKILL.md b/_skills/testing-debugging/SKILL.md
@@ -0,0 +1,17 @@
+---
+name: testing-debugging
+description: Ensuring software correctness and reliability by writing automated tests, using quality assurance tools, and systematically debugging issues.
+version: '1.0'
+---
+# Testing & Debugging
+
+Writing robust software requires verifying that it works as intended. Developers are expected to build automated tests for their code and use debugging skills to quickly isolate issues. Thorough testing (unit tests, integration tests, etc.) gives confidence that changes won’t break existing functionality. It’s far cheaper to catch bugs early with tests or static analysis than in production.
+
+## Examples
+- Implementing a suite of unit tests for each new feature, and running them in a CI pipeline on each commit.
+- Using a debugger or logging to track down the root cause of a bug, then adding a test to prevent regression.
+
+## Guidelines
+- **Automated Testing:** Write tests to cover your code’s behavior – unit tests for individual functions, integration tests for components, etc. Aim for meaningful coverage of critical paths and edge cases. This ensures your code is correct and stays correct as it evolves.
+- **Quality Tools:** Employ linters and formatters to catch issues and enforce standards automatically. For example, use ESLint or Prettier so style issues are fixed upfront, freeing code reviews to focus on logic. Use static analysis and security scanners to find flaws early.
+- **Systematic Debugging:** When bugs arise, debug methodically. Reproduce issues in a controlled environment, use breakpoints or logging to inspect state, and bisect changes if necessary. Once fixed, add tests for those cases to avoid regressions. A disciplined debugging approach saves time and builds more reliable software.
PATCH

echo "Gold patch applied."
