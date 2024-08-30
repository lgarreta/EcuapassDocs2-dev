// Functions for autocomplete in document forms
//
// Get last CSRF token (after redirects)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Create autocomplete for an entity
function createAutocomplete (entity) {
	const csrftoken = getCookie('csrftoken');

	let inputSelector = entity.inputSelector
	let sourceUrl     = entity.sourceUrl
	
	$(inputSelector).autocomplete({
		// List of autocomplete options
		source: function (request, response) {
			$.ajax({ url: sourceUrl, type:'POST', dataType: 'json', data: {query: request.term},

				beforeSend: function (xhr, settings) {
					// Include the CSRF token in the request headers
					xhr.setRequestHeader("X-CSRFToken", csrftoken);
				},

				success: function (data) {
					responseData = entity.onAjaxSuccess (data)
					response (responseData)
				}
			});
		},
		minLength: 2, 
		position: { my: "left top", at: "center top", collision: "none" }, // Customize the position
		select: function (event, ui) {
			entity.onItemSelected (ui)
			// Prevent the default behavior of filling the input with the selected value
			return false;
		}
	});
}

// Return array of selected textAreas according to className
function getTextAreasByClassName (className) {
	let selectedTextAreas = []
	textAreas.forEach (textArea => {
		if (textArea.className === className) {
			selectedTextAreas.push (textArea)
		}
	});
	return (selectedTextAreas);
}

// Set autocomplete for document according to doc type
// Doc types: "cartaporte", "manifiesto", "declaración
function setAutocompleteForDocument (documentType) {
		// Clientes
		let clienteInputs = getTextAreasByClassName ("input_cliente")
		console.log ("clienteInput:", clienteInputs)
		clienteInputs.forEach (inputName => {
			createAutocomplete(new AutoComplete (inputName, 'opciones-cliente')) 
		});
	
		// Ciudad-Pais. Fecha
		let inputsLugarFecha = getTextAreasByClassName ("input-lugar-fecha")
		inputsLugarFecha.forEach (inputName => {
			createAutocomplete(new AutoComplete (inputName, 'opciones-lugar-fecha' )) 
		});

		// Ciudad-Pais
		let inputsLugar = getTextAreasByClassName ("input_lugar")
		inputsLugar.forEach (inputName => {
			createAutocomplete(new AutoComplete (inputName, 'opciones-lugar' )) 
		});

		// Cartaportes
		let cartaporteInputs = getTextAreasByClassName ("input_cartaporte")
		cartaporteInputs.forEach (inputName => {
			createAutocomplete(new AutoCompleteCartaporte (inputName, 'opciones-cartaporte/', documentType)) 
		});


		// Vehiculo
		let vehiculoInputs = getTextAreasByClassName ("input_placaPais")
		vehiculoInputs.forEach (inputName => {
			createAutocomplete(new AutoCompletePlacaPais (inputName, 'opciones-vehiculo/')) 
		});

		// Conductor
		let conductorInputs = getTextAreasByClassName ("input_conductor")
		conductorInputs.forEach (inputName => {
			createAutocomplete(new AutoCompleteConductor (inputName, 'opciones-conductor')) 
		});
}

//----------------------------------------------------------------------
//---------------- Autocomplet for "cartaporte" ------------------------
//----------------------------------------------------------------------

//-- General class for autocomplete only with the value of the option
class AutoComplete {
	// Init with input element and source URL which is handles in views
	constructor (inputSelector, sourceUrl, documentType=null) {
		let inputId        = "#" + inputSelector
		this.inputSelector = inputSelector;
		this.sourceUrl     = sourceUrl;
		this.fullData      = null;
		this.documentType  = documentType; 
	}

	// When ajax query is succesfull, set items
	onAjaxSuccess (data) {
		this.fullData = data;
		let flatData = [];
		for (let i=0; i < data.length; i++) {
			flatData.push (data[i] ["itemLine"])
		}
		return flatData;
	}

	// When an item is selected, populate the textarea 
	onItemSelected (ui) {
		let index = ui.item.value.split (".")[0]
		let text = this.fullData [index]["itemText"]
		$(this.inputSelector).val (text);
	}
}

//-------------------------------------------------------------------
//-- Autocomplet for "cartaporte" -----------------------------------
//-------------------------------------------------------------------
class AutoCompleteCartaporte extends AutoComplete {
	// When a cartaporte number is selected, populate related inputs
	onItemSelected (ui) {
		let index = ui.item.value.split (".")[0]
		let text = this.fullData [index]["itemText"]
		let values = text.split ("||");
		
		let docInputsIds = null;
		if (this.documentType === "MANIFIESTO")
			docInputsIds = ["28","29","30","31","32_1","32_3","33_1","34","32_2","32_4","33_2"];
		else if (this.documentType === "DECLARACION")
			docInputsIds = ["15","16","17","18","19_1","19_3","20_1","21","19_2","19_4","20_2"];
		else { 
			return null
		}

		for (let i=0; i < docInputsIds.length; i++) {
			let txtId = "txt" + docInputsIds [i]
			document.getElementById (txtId).value = values [i]
		}
	}
}

//-- AutoComplete for Vehiculo inputs
class AutoCompletePlacaPais extends AutoComplete {
	// When an item is selected, populate the textarea 
	onItemSelected (ui) {
		let index = ui.item.value.split (".")[0]
		let text = this.fullData [index]["itemText"]
		let values = text.split ("||");
		let input = this.inputSelector
		if (input.id === "txt06") {
			document.getElementById("txt04").value = values [0]
			document.getElementById("txt05").value = values [1]
			document.getElementById("txt06").value = values [2]
			document.getElementById("txt07").value = values [3]
		}else {
			document.getElementById("txt09").value = values [0]
			document.getElementById("txt10").value = values [1]
			document.getElementById("txt11").value = values [2]
			document.getElementById("txt12").value = values [3]
		}
	}
}

//-- Autocomplete Conductor inputs
class AutoCompleteConductor extends AutoComplete {
	// When an item is selected, populate the textarea 
	onItemSelected (ui) {
		let index = ui.item.value.split (".")[0]
		let text = this.fullData [index]["itemText"]
		let values = text.split ("||");
		let input = this.inputSelector
		if (input.id === "txt13") {
			document.getElementById("txt13").value = values [0]
			document.getElementById("txt14").value = values [1]
			document.getElementById("txt15").value = values [2]
			document.getElementById("txt16").value = values [3]
			document.getElementById("txt17").value = values [4]
		}else {
			document.getElementById("txt18").value = values [0]
			document.getElementById("txt19").value = values [1]
			document.getElementById("txt20").value = values [2]
			document.getElementById("txt21").value = values [3]
			document.getElementById("txt22").value = values [4]
		}
	}
}
