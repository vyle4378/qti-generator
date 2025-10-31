const textareas = document.querySelectorAll("textarea");
const userInput = document.getElementById("userInput");
const generateButton = document.getElementById("generateButton");
const responseArea = document.getElementById("responseArea");
const convertButton = document.getElementById("convertButton");
const formatButton = document.getElementById("formatButton");

async function generateProblems(userInput) {
  const message = userInput.value;
  const response = await fetch("/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  const data = await response.json();
  responseArea.value = data.problems;
  console.log("done generating problems");
  adjustTextareaHeight();
}

async function formatProblems(responseArea) {
  const problems = responseArea.value;
  const response = await fetch("/format", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ problems }),
  });

  const data = await response.json();
  responseArea.value = data.problems;
  console.log("done formatting problems");
  adjustTextareaHeight();
}

async function convertProblems() {
  const problems = responseArea.value;
  const zipName = document.getElementById("zipName").value;

  const response = await fetch("/convert", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ problems }),
  });

  const zip = await response.blob();
  if (zip.type !== "application/zip") {
    alert(
      "Error: There is a formatting issue. Please fix it and try again. You can click on the 'Format' button if needed."
    );
    return;
  } else {
    const url = URL.createObjectURL(zip);
    const a = document.createElement("a");
    a.href = url;
    a.download = zipName + ".zip";
    a.click();
    a.remove(); // Removes the hidden "a" element from the html
    URL.revokeObjectURL(url); // Frees up memory used by the blob URL
    console.log("done converting problems");
  }
}

function adjustTextareaHeight() {
  textareas.forEach((textarea) => {
    textarea.addEventListener("input", () => {
      textarea.style.height = "auto";
      textarea.style.height = textarea.scrollHeight - 20 + "px";
    });
  });
}

generateButton.addEventListener("click", () => {
  if (userInput.value !== "") {
    generateProblems(userInput);
  } else {
    alert("Please enter a topic for problem generation");
  }
});

formatButton.addEventListener("click", () => {
  if (responseArea.value !== "") {
    formatProblems(responseArea);
  } else {
    alert("Please enter problems to format");
  }
});

convertButton.addEventListener("click", () => {
  if (responseArea.value !== "") {
    convertProblems();
  } else {
    alert("Please enter problems to convert");
  }
});

adjustTextareaHeight();
