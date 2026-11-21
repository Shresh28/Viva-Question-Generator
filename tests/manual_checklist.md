# Manual testing checklist

Run the app with one representative, searchable PDF from each domain. Reports are sent to the local Ollama service on your computer.

- [ ] Machine Learning project report
- [ ] Web Development project report
- [ ] IoT project report
- [ ] Data Science project report
- [ ] A different domain (for example, cybersecurity, mobile apps, or embedded systems)

For each report, record the filename and check:

- [ ] Correct filename and PDF page count are shown.
- [ ] Extracted text is readable; scanned PDFs receive an OCR recommendation.
- [ ] The extracted title, domain, objective, and technologies match the report.
- [ ] Questions differ meaningfully by report and refer to its details.
- [ ] Answers are relevant, concise, and flag details the report does not specify.
- [ ] Exactly 15 questions appear, with exactly 5 per difficulty.
- [ ] No questions repeat or merely paraphrase one another.
- [ ] Hard questions require more reasoning than Easy questions.
- [ ] TXT and PDF downloads open and contain all questions and answers.
- [ ] Regenerate works and a new PDF upload clears stale results.

Do not mark these checks complete until they have actually been run. Automated tests use mock responses and do not verify live model quality.

