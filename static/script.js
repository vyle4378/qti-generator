const textareas = document.querySelectorAll("textarea");
const userInput = document.getElementById("userInput");
const generateButton = document.getElementById("generateButton");
const responseArea = document.getElementById("responseArea");
const convertButton = document.getElementById("convertButton");

async function generateProblems(input) {
  const message = input.value;
  const response = await fetch("/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  const data = await response.json();
  responseArea.value = data.problems;
  adjustTextareaHeight();
}

async function convertProblems() {
  const zipName = document.getElementById("zipName").value;

  // Format the problems if they are not already formatted. Fix any wrong answers or typos.
  generateProblems(responseArea);
  const problems = responseArea.value;

  const response = await fetch("/convert", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ problems }),
  });

  const zip = await response.blob();
  const url = URL.createObjectURL(zip);
  const a = document.createElement("a");
  a.href = url;
  a.download = zipName + ".zip";
  a.click();
  a.remove(); // Removes the hidden "a" element from the html
  URL.revokeObjectURL(url); // Frees up memory used by the blob URL
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

convertButton.addEventListener("click", () => {
  if (responseArea.value !== "") {
    convertProblems();
  } else {
    alert("Please enter problems to convert");
  }
});

adjustTextareaHeight();
