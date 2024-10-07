// Enable or disalble buttons from nav bar in document form

function enableDisableDocButtons (document, docNumber) {
	//let docNumber = document.getElementById ("numero")
	console.log (">>> DocNumber:", docNumber)
	if (docNumber.value === "" || docNumber.value === "CLON") {
		console.log (">>> Disabling Buttons...")
		document.getElementById("boton_pdf_original").setAttribute("disabled", "disabled");
		document.getElementById("boton_pdf_copia").setAttribute("disabled", "disabled");
		document.getElementById("boton_pdf_paquete").setAttribute("disabled", "disabled");
		document.getElementById("boton_clonar").setAttribute("disabled", "disabled");
		document.getElementById("boton_detalle").setAttribute("disabled", "disabled");
	}else {
		console.log (">>> Enabling Buttons...")
		document.getElementById("boton_pdf_original").removeAttribute("disabled");
		document.getElementById("boton_pdf_copia").removeAttribute("disabled");
		document.getElementById("boton_pdf_paquete").removeAttribute("disabled");
		document.getElementById("boton_clonar").removeAttribute("disabled");
		document.getElementById("boton_detalle").removeAttribute("disabled");
	}
}

