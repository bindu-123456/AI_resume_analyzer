console.log("AI Resume Analyzer is working!");

// Load job roles from the Flask backend
async function loadJobs() {
    const jobDropdown = document.getElementById("job");

    try {
        const response = await fetch("/jobs");

        if (!response.ok) {
            throw new Error("Could not load jobs");
        }

        const jobs = await response.json();

        jobDropdown.innerHTML =
            '<option value="">-- Select a Job --</option>';

        Object.keys(jobs).forEach(function (jobId) {
            const option = document.createElement("option");

            option.value = jobId;
            option.textContent = jobs[jobId].title;

            jobDropdown.appendChild(option);
        });

    } catch (error) {
        console.error("Error loading jobs:", error);

        jobDropdown.innerHTML =
            '<option value="">Could not load jobs</option>';
    }
}

loadJobs();

document.getElementById("resumeForm").addEventListener(
    "submit",
    async function (event) {
        event.preventDefault();

        const resumeFile =
            document.getElementById("resume").files[0];

        const jobId =
            document.getElementById("job").value;

        const result = document.getElementById("result");

        // Validate the resume
        if (!resumeFile) {
            result.textContent = "Please select a resume PDF.";
            return;
        }

        if (!resumeFile.name.toLowerCase().endsWith(".pdf")) {
            result.textContent = "Please upload a PDF file.";
            return;
        }

        // Validate the selected job
        if (!jobId) {
            result.textContent = "Please select a job role.";
            return;
        }

        // Send resume and job ID to Flask
        const formData = new FormData();

        formData.append("resume", resumeFile);
        formData.append("jobId", jobId);

        result.innerHTML = `
            <div class="loading-card">
                <h3>Analyzing Your Resume...</h3>
                <p>Comparing your resume with the selected job requirements.</p>
            </div>
        `;

        try {
            const response = await fetch("/analyze", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                result.textContent =
                    data.error || "Analysis failed.";
                return;
            }

            if (
                typeof data.match_percentage !== "number" ||
                !Array.isArray(data.matching_skills) ||
                !Array.isArray(data.missing_skills)
            ) {
                result.textContent =
                    "Analysis results are incomplete. Please check app.py.";
                return;
            }

            result.innerHTML = "";

            // Results heading
            const heading = document.createElement("h2");
            heading.textContent = "Resume Analysis Results";
            result.appendChild(heading);

            // Selected job title
            const jobTitle = document.createElement("p");
            jobTitle.className = "selected-job";
            jobTitle.textContent =
                "Selected Job: " + (data.job_title || "Unknown");
            result.appendChild(jobTitle);

            // Match score card
            const scoreCard = document.createElement("div");
            scoreCard.className = "score-card";

            const scoreTitle = document.createElement("h3");
            scoreTitle.textContent = "Your Resume Match";

            const scoreValue = document.createElement("div");
            scoreValue.className = "score-value";

            const percentage = Math.max(
                0,
                Math.min(100, data.match_percentage)
            );

            scoreValue.textContent = percentage + "%";

            const scoreMessage = document.createElement("p");

            if (percentage >= 75) {
                scoreMessage.textContent =
                    "Your resume matches many of the identified skills.";
            } else if (percentage >= 40) {
                scoreMessage.textContent =
                    "Review the missing skills to identify areas for improvement.";
            } else {
                scoreMessage.textContent =
                    "Consider developing relevant skills for this role.";
            }

            const progressTrack = document.createElement("div");
            progressTrack.className = "progress-track";

            const progressBar = document.createElement("div");
            progressBar.className = "progress-bar";
            progressBar.style.width = percentage + "%";

            progressTrack.appendChild(progressBar);

            scoreCard.appendChild(scoreTitle);
            scoreCard.appendChild(scoreValue);
            scoreCard.appendChild(progressTrack);
            scoreCard.appendChild(scoreMessage);

            result.appendChild(scoreCard);

            // Skills container
            const skillsContainer = document.createElement("div");
            skillsContainer.className = "skills-container";

            // Matching skills
            const matchingCard = document.createElement("div");
            matchingCard.className = "skill-card matching-card";

            const matchingHeading = document.createElement("h3");
            matchingHeading.textContent =
                "✅ Matching Skills (" +
                data.matching_skills.length + ")";

            const matchingList = document.createElement("ul");

            if (data.matching_skills.length > 0) {
                data.matching_skills.forEach(function (skill) {
                    const item = document.createElement("li");
                    item.textContent = skill;
                    matchingList.appendChild(item);
                });
            } else {
                const item = document.createElement("li");
                item.textContent = "No matching skills found.";
                matchingList.appendChild(item);
            }

            matchingCard.appendChild(matchingHeading);
            matchingCard.appendChild(matchingList);

            // Missing skills
            const missingCard = document.createElement("div");
            missingCard.className = "skill-card missing-card";

            const missingHeading = document.createElement("h3");
            missingHeading.textContent =
                "📌 Missing Skills (" +
                data.missing_skills.length + ")";

            const missingList = document.createElement("ul");

            if (data.missing_skills.length > 0) {
                data.missing_skills.forEach(function (skill) {
                    const item = document.createElement("li");
                    item.textContent = skill;
                    missingList.appendChild(item);
                });
            } else {
                const item = document.createElement("li");
                item.textContent =
                    "No missing skills detected from this checklist.";
                missingList.appendChild(item);
            }

            missingCard.appendChild(missingHeading);
            missingCard.appendChild(missingList);

            skillsContainer.appendChild(matchingCard);
            skillsContainer.appendChild(missingCard);

            result.appendChild(skillsContainer);
            // Resume Improvement Suggestions
const suggestionsCard = document.createElement("div");
suggestionsCard.className = "skill-card";
suggestionsCard.style.marginTop = "20px";

const suggestionsHeading = document.createElement("h3");
suggestionsHeading.textContent = "💡 Resume Improvement Suggestions";
suggestionsCard.appendChild(suggestionsHeading);

const suggestionsList = document.createElement("ul");

if (data.suggestions && data.suggestions.length > 0) {
    data.suggestions.forEach(function (suggestion) {
        const item = document.createElement("li");
        item.textContent = suggestion;
        suggestionsList.appendChild(item);
    });
} else {
    const item = document.createElement("li");
    item.textContent =
        "No suggestions available. Your resume covers the skills checked.";
    suggestionsList.appendChild(item);
}

suggestionsCard.appendChild(suggestionsList);
result.appendChild(suggestionsCard);

            // Total required skills
            const total = document.createElement("p");
            total.className = "total-skills";
            total.textContent =
                "Required skills checked: " +
                (data.total_required_skills ?? "Not available");

            result.appendChild(total);

            
            // Download Analysis Report button
            const downloadButton = document.createElement("button");
            downloadButton.type = "button";
            downloadButton.className = "analyze-again-button";
            downloadButton.textContent = "Download Analysis Report";

            downloadButton.textContent = "Download PDF Report";

downloadButton.addEventListener("click", function () {
    if (!window.jspdf || !window.jspdf.jsPDF) {
        alert("PDF library not loaded. Please refresh the page.");
        return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    let y = 50;

    // Professional header
    doc.setFillColor(20, 40, 75);
    doc.rect(0, 0, 210, 38, "F");

    doc.setTextColor(255, 255, 255);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(20);
    doc.text("AI RESUME ANALYZER", 15, 17);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.text("Resume Match and Improvement Report", 15, 27);

    // Job role
    doc.setTextColor(40, 40, 40);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text("Job Role: " + (data.job_title || "Not available"), 15, y);
    y += 15;

    // Match score card
    doc.setFillColor(232, 240, 255);
    doc.roundedRect(15, y - 7, 180, 23, 3, 3, "F");

    doc.setTextColor(20, 55, 110);
    doc.setFontSize(18);
    doc.text("Resume Match: " + data.match_percentage + "%", 22, y + 7);
    y += 28;

    // Add sections and handle long content
    function addSection(title, items) {
        if (y > 255) {
            doc.addPage();
            y = 20;
        }

        doc.setTextColor(20, 55, 110);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(16);
        doc.text(title, 15, y);
        y += 8;

        

        doc.setTextColor(50, 50, 50);
        doc.setFont("helvetica", "normal");
        doc.setFontSize(12);

        const lines = items.length ? items : ["None identified."];

        lines.forEach(function (item, index) {
            const text = items.length
                ? (index + 1) + ". " + item
                : item;

            const wrapped = doc.splitTextToSize(text, 175);

            if (y + wrapped.length * 6 > 275) {
                doc.addPage();
                y = 20;
            }

            doc.text(wrapped, 18, y);
            y += wrapped.length * 6 + 2;
        });

        y += 7;
    }

    addSection("Matching Skills", data.matching_skills || []);
    addSection("Missing Skills", data.missing_skills || []);
    addSection(
        "Resume Improvement Suggestions",
        data.suggestions || []
    );

    // Summary and disclaimer
    if (y > 260) {
        doc.addPage();
        y = 20;
    }

    doc.setTextColor(50, 50, 50);
    doc.setFontSize(10);
    doc.text(
        "Total required skills checked: " + data.total_required_skills,
        15,
        y
    );

    y += 10;

    doc.setFontSize(9);
    doc.setTextColor(100, 100, 100);

    const note = doc.splitTextToSize(
        "Note: This is an approximate keyword-based match, " +
        "not a guarantee of job suitability.",
        180
    );

    doc.text(note, 15, y);

    // Download PDF
    doc.save("AI_Resume_Analysis_Report.pdf");
});

result.appendChild(downloadButton);
            // Analyze another resume button
            const resetButton = document.createElement("button");
            resetButton.type = "button";
            resetButton.className = "analyze-again-button";
            resetButton.textContent = "Analyze Another Resume";

            resetButton.addEventListener("click", function () {
                document.getElementById("resumeForm").reset();
                result.innerHTML = "";

                document.getElementById("resumeForm").scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            });

            result.appendChild(resetButton);

        } catch (error) {
            console.error("Error:", error);

            result.textContent =
                "Unable to connect to Flask. Check whether the server is running.";
        }
    }
);