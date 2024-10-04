/* Handle char inpus in textareas:
	Convert to uppercase
	Control maxlines
*/
function handleInput (event) {
	textArea = event.target;
	convertToUpperCase (textArea);
	controlMaxlines (textArea);
    handleTextAreaInput (textArea, event)
}

// Save the current cursor position
function convertToUpperCase (textArea) {
	var start = textArea.selectionStart;
	var end = textArea.selectionEnd;
	// Convert the text to uppercase and set it back to the textArea
	textArea.value = textArea.value.toUpperCase();
	// Restore the cursor position
	textArea.setSelectionRange(start, end);
}

// Control maximum number of lines
function controlMaxlines (textarea) {
	MAXLINES = inputsParameters [textArea.id]["maxLines"];
    console.log (">>> MAXLINES:", MAXLINES)
	lines = textArea.value.split('\n'); 
	if (lines.length > MAXLINES) 
		textArea.value = lines.slice (0, MAXLINES).join('\n');
}

// Function to handle typing in the textarea
maxCharsPerLine = 20
function handleTextAreaInput (textArea, event) {
	const lines = textArea.value.split('\n');
	const cursorPosition = textArea.selectionStart;

	let currentLine = getCurrentLine(textArea);
	let currentLineLength = currentLine.length;

	if (currentLineLength > maxCharsPerLine) {
		// Show popup and prevent further typing on this line
		showMaxCharMessage();

		// Revert the input change
		textArea.value = textArea.value.substring(0, cursorPosition - 1) + textArea.value.substring(cursorPosition);

		// Move cursor back to original position after removing the last character
		textArea.setSelectionRange(cursorPosition - 1, cursorPosition - 1);
	}
}


// Show the popup message and play bell sound
function showMaxCharMessage() {
	popup.style.display = 'block';  // Show the popup
	setTimeout(() => {
		popup.style.display = 'none';  // Hide popup after 2 seconds
	}, 2000);
	bellSound.play();  // Play bell sound
}

// Function to get the current line content based on cursor position
function getCurrentLine(textArea) {
	const cursorPosition = textArea.selectionStart;
	const textUpToCursor = textArea.value.substring(0, cursorPosition);
	const linesUpToCursor = textUpToCursor.split('\n');

	return linesUpToCursor[linesUpToCursor.length - 1];  // Return current line
}

// Show the popup message and play bell sound
function showMaxCharMessage() {
	popup.style.display = 'block';  // Show the popup
	setTimeout(() => {
		popup.style.display = 'none';  // Hide popup after 2 seconds
	}, 2000);
	bellSound.play();  // Play bell sound
}


