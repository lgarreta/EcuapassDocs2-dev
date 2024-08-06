// Enable or disalble buttons from nav bar in document form

function enableDisableDocButtons (enableFlag) {
	if (enableFlag === "ENABLE") {
		document.getElementById("boton_pdf_original").removeAttribute("disabled");
		document.getElementById("boton_pdf_copia").removeAttribute("disabled");
		document.getElementById("boton_pdf_paquete").removeAttribute("disabled");
		document.getElementById("boton_clonar").removeAttribute("disabled");
	}else {
		document.getElementById("boton_pdf_original").setAttribute("disabled", "disabled");
		document.getElementById("boton_pdf_copia").setAttribute("disabled", "disabled");
		document.getElementById("boton_pdf_paquete").setAttribute("disabled", "disabled");
		document.getElementById("boton_clonar").setAttribute("disabled", "disabled");
	}
}

