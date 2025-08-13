document.addEventListener('DOMContentLoaded', () => {
    const serviciosTbody = document.getElementById('servicios-tbody');
    const addServicioBtn = document.getElementById('add-servicio');

    function calcularTotales() {
        let total = 0;

        serviciosTbody.querySelectorAll('tr').forEach(fila => {
            const cantidadInput = fila.querySelector('input[name^="cantidad"]');
            const precioInput = fila.querySelector('input[name^="precio"]');

            if (!cantidadInput || !precioInput) return;

            const cantidad = parseFloat(cantidadInput.value) || 0;
            const precio = parseFloat(precioInput.value) || 0;
            const subtotal = cantidad * precio;

            const subtotalTd = fila.querySelector('td:nth-child(5)');
            if (subtotalTd) {
                subtotalTd.textContent = `$${subtotal.toLocaleString('es-CL')}`;
            }

            total += subtotal;
        });

        const totalEl = document.querySelector('.text-xl.font-bold');
        if (totalEl) {
            totalEl.textContent = `$${total.toLocaleString('es-CL')} CLP`;
        }
    }

    function agregarEventosFila(fila) {
        fila.querySelectorAll('input[name^="cantidad"], input[name^="precio"]').forEach(input => {
            input.addEventListener('input', calcularTotales);
        });

        const btnEliminar = fila.querySelector('.remove-row');
        if (btnEliminar) {
            btnEliminar.addEventListener('click', () => {
                fila.remove();

                if (serviciosTbody.children.length === 0) {
                    const noServicios = document.createElement('tr');
                    noServicios.id = 'no-servicios-row';
                    noServicios.innerHTML = `<td colspan="6" class="p-4 text-center text-gray-500">No hay servicios registrados</td>`;
                    serviciosTbody.appendChild(noServicios);
                }

                calcularTotales();
            });
        }
    }

    // Agregar nuevo servicio
    addServicioBtn.addEventListener('click', () => {
        const noServiciosRow = document.getElementById('no-servicios-row');
        if (noServiciosRow) noServiciosRow.remove();

        const nuevaFila = document.createElement('tr');
        nuevaFila.classList.add('nuevo-servicio');
        nuevaFila.innerHTML = `
            <td class="p-2">
                <select name="tipo_nuevo[]" class="w-full border rounded p-1">
                    <option value="Servicio">Servicio</option>
                    <option value="Producto">Producto</option>
                </select>
            </td>
            <td class="p-2">
                <input type="text" name="descripcion_nuevo[]" placeholder="Descripción" required
                    class="w-full border rounded p-1" />
            </td>
            <td class="p-2">
                <input type="number" name="cantidad_nuevo[]" placeholder="5" min="1" required
                    class="w-16 border rounded p-1 text-center" />
            </td>
            <td class="p-2">
                <input type="number" name="precio_nuevo[]" placeholder="10000" min="0" step="1" required
                    class="w-full border rounded p-1 text-right" />
            </td>
            <td class="p-2 text-right">$0</td>
            <td class="p-2 text-center">
                <button type="button" class="remove-row text-red-500">
                    <i class="fas fa-trash-alt"></i> Eliminar
                </button>
            </td>
        `;
        serviciosTbody.appendChild(nuevaFila);
        agregarEventosFila(nuevaFila);
    });

    // Inicializar eventos para las filas existentes
    serviciosTbody.querySelectorAll('tr').forEach(fila => agregarEventosFila(fila));

    // Calcular totales al cargar
    calcularTotales();
});
