document.addEventListener("DOMContentLoaded", () => {
    const downloadBtn = document.getElementById("descargar-pdf");
    if (!downloadBtn) return;

    downloadBtn.addEventListener("click", () => {
        // Obtener fecha actual formateada
        const today = new Date();
        const formattedDate = today.toLocaleDateString('es-CL', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });

        const clienteNombre = document.getElementById("cliente-nombre")?.textContent.trim() || "N/A";
        const clienteTelefono = document.getElementById("cliente-telefono")?.textContent.trim() || "N/A";
        const cliente = `${clienteNombre} (${clienteTelefono})`;

        const vehiculoSelect = document.getElementById("vehiculo-select");
        const vehiculo = vehiculoSelect?.selectedOptions[0]?.textContent.trim() || "N/A";
        const motivo = document.getElementById("motivo")?.value.trim() || "Sin motivo";
        const observacion = document.querySelector('[name="observacion"]')?.value.trim() || "Sin observación";

        // Insertar datos en plantilla
        document.getElementById("pdf-cliente").textContent = cliente;
        document.getElementById("pdf-vehiculo").textContent = vehiculo;
        document.getElementById("pdf-fecha").textContent = formattedDate;
        document.getElementById("pdf-motivo").textContent = motivo;
        document.getElementById("pdf-observacion").textContent = observacion;

        // Ocultar número de ticket
        document.querySelector('p:has(> #pdf-numero)').style.display = "none";

        const serviciosBody = document.getElementById("pdf-servicios");
        serviciosBody.innerHTML = "";

        let total = 0;

        // 🚀 Procesar servicios existentes (editables)
        document.querySelectorAll("#servicios-tbody tr").forEach(row => {
            const tipo = row.querySelector('[name="tipo[]"]')?.value.trim();
            const desc = row.querySelector('[name="descripcion[]"]')?.value.trim();
            const cant = parseFloat(row.querySelector('[name="cantidad[]"]')?.value) || 0;
            const precio = parseFloat(row.querySelector('[name="precio_unitario[]"]')?.value) || 0;
            const subtotal = cant * precio;

            if (!desc || cant <= 0 || precio <= 0) return;

            total += subtotal;

            const tr = document.createElement("tr");
            tr.innerHTML = `
        <td style="padding: 12px 10px; border: 1px solid #334155; text-align: left;">${tipo}</td> 
        <td style="padding: 12px 10px; border: 1px solid #334155; text-align: left;">${desc}</td>
        <td style="padding: 12px 10px; border: 1px solid #334155;; text-align: center;">${cant}</td>
        <td style="padding: 12px 10px; border: 1px solid #334155; text-align: right;">$${precio.toLocaleString("es-CL")}</td>
        <td style="padding: 12px 10px; border: 1px solid #334155; text-align: right;">$${subtotal.toLocaleString("es-CL")}</td>
    `;
            serviciosBody.appendChild(tr);
        });

        // Actualizar total (usando pdf-subtotal como el total final)
        document.getElementById("pdf-subtotal").textContent = total.toLocaleString("es-CL");

        // Mostrar la plantilla y generar PDF
        const pdfTemplate = document.getElementById("pdf-template");
        pdfTemplate.style.display = "block";

        // Configuración de html2pdf
        const opt = {
            margin: 10,
            filename: `cotizacion_${cliente.replace(/\s+/g, "_")}_${formattedDate.replace(/\//g, "-")}.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };

        // Generar PDF
        html2pdf().set(opt).from(pdfTemplate).save().then(() => {
            pdfTemplate.style.display = "none";
            document.querySelector('p:has(> #pdf-numero)').style.display = "";
        });
    });
});
