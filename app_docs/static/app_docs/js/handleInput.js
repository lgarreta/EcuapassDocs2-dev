/* Handle char inpus in textareas:
	Convert to uppercase
	Control maxlines
*/
function handleInput (event) {
	textArea = event.target;
	convertToUpperCase (textArea);
	controlMaxlines (textArea);
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
	lines = textArea.value.split('\n'); 
	if (lines.length > MAXLINES) 
		textArea.value = lines.slice (0, MAXLINES).join('\n');
}


// ------------------------------------------------------------------
// ----- Other fuctions --------------------------------------------- 
// ------------------------------------------------------------------
	//
// Scripts to handle input manually: MAXCHARS, NEWLINES, WRAPWORD
function getWrappedText (textarea) {
	//var textarea = document.getElementById('myTextarea');
    var text = textarea.value;
	console.log ("+++ text:", text)
    
    // Calculate wrapped lines
    var cols = textarea.cols; // Number of columns defined in the textarea
    var lines = text.split('\n'); // Split the text by newlines

    var wrappedText = lines.map(line => {
        let result = [];
        for (let i = 0; i < line.length; i += cols) {
            result.push (line.substring(i, i + cols));
        }		
        return result.join('\n');
    }).join('\n');

    console.log(wrappedText); // Send this wrapped text to your server or use it in PDF generation
}


// Control max number of lines and chars according to className
function old_handleInput (event) {
	textArea = event.target;
	convertToUpperCase (textArea);

	MAXLINES = inputsParameters [textArea.id]["maxLines"];
	//MAXCHARS = inputsParameters [textArea.id]["maxChars"] * 3.6;
	MAXCHARS = inputsParameters [textArea.id]["maxChars"];

	// Control maximum number of chars
	//lines = pdf.splitTextToSize (textArea.value, MAXCHARS);
	//textArea.value = lines.join("\n");
	var lines = textArea.value.split('\n');

	for (var i = 0; i < lines.length; i++) {
		if (lines[i].length > MAXCHARS) {
			// Truncate the line to the maximum allowed characters
			var remainingChars = lines[i].substring(MAXCHARS);
			lines[i] = lines[i].substring(0, MAXCHARS);
			// Move the remaining characters to the next line
			lines.splice(i + 1, 0, remainingChars);
		}
	}
	// Join the modified lines and set the textarea value
	textArea.value = lines.join('\n');			

	// Control maximum number of lines
	text = textArea.value;
	lines = text.split('\n'); 
	if (lines.length > MAXLINES) 
		textArea.value = lines.slice (0, MAXLINES).join('\n');
}

// NOT USED For handline manually MAXCHARS and insert newlines
function handleInput_MAXCHARS (event) {
		textArea = event.target;
		convertToUpperCase (textArea);

		MAXLINES = inputsParameters [textArea.id]["maxLines"];
		//MAXCHARS = inputsParameters [textArea.id]["maxChars"] * 3.6;
		MAXCHARS = inputsParameters [textArea.id]["maxChars"];
		
        // Get the current value of the textarea
        let value = textArea.value;

		//value = value.replace(/\n/g, '');

        // Get the current caret position
        let cursorPosition = textArea.selectionStart;

        // Split the text into lines
        let lines = value.split('\n');

        // Variable to store the adjusted text
        let adjustedText = '';
        let newCursorPosition = cursorPosition;

        // Track the total length processed so far
        let charCount = 0;

		//lines = lines.map (line => line.replace(/\n$/, ''));
        // Adjust each line to ensure it doesn't exceed MAXCHARS
        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];
            while (line.length > MAXCHARS) {
                // Split the line at MAXCHARS
                let splitLine = line.substring(0, MAXCHARS);
                adjustedText += splitLine + '\n';
                line = line.substring(MAXCHARS);
				line = ""
                // Adjust cursor position if needed
                if (charCount + MAXCHARS < cursorPosition) {
                    newCursorPosition++;
                }
                charCount += MAXCHARS + 1; // +1 for the newline character
            }
            adjustedText += line;
            charCount += line.length;
			// Add newline if it's not the last line
            if (i < lines.length - 1) {
                adjustedText += '\n';
            }
			// If the new text length differs from the old one, update the cursor position
        	if (adjustedText.length !== value.length) {
            	newCursorPosition += adjustedText.length - value.length;
        	}
        }

        // Update the textarea value and restore the caret position
        textArea.value = adjustedText;
        textArea.setSelectionRange(newCursorPosition, newCursorPosition);
    }

