document.addEventListener('DOMContentLoaded', () => {
    const serviciosTbody = document.getElementById('servicios-tbody');
    const noServiciosRow = document.getElementById('no-servicios-row');

    // Agregar nuevo servicio
    document.getElementById('add-servicio').addEventListener('click', () => {
        // Si existe fila "No hay servicios", la removemos
        if (noServiciosRow) noServiciosRow.remove();

        const nuevaFila = document.createElement('tr');
        nuevaFila.classList.add('nuevo-servicio');
        nuevaFila.innerHTML = `
            <td class="px-4 py-3 whitespace-nowrap">
                <select name="tipo[]"
                        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-hyf-accent focus:border-hyf-accent">
                        <option value="Servicio">
                            Servicio
                        </option>
                        <option value="Producto">
                            Producto
                        </option>
                    </select>
            </td>
            <td class="px-4 py-3 whitespace-nowrap text-right">
                <input type="text" name="descripcion_nuevo[]" placeholder="Descripción" required
                    class="w-full p-2 border border-gray-300 rounded focus:ring-hyf-accent focus:border-hyf-accent" />
            </td>
            <td class="px-4 py-3 whitespace-nowrap text-center">
                <input type="number" name="cantidad_nuevo[]" placeholder="5" min="1" required
                    class="w-16 p-2 border border-gray-300 rounded text-center focus:ring-hyf-accent focus:border-hyf-accent" />
            </td>
            <td class="px-4 py-3 whitespace-nowrap text-right">
                <div class="relative">
                    <span class="absolute left-3 top-2 text-gray-500">$</span>
                    <input type="number" name="precio_nuevo[]" placeholder="10000" min="0" required
                        class="w-full pl-8 pr-3 p-2 border border-gray-300 rounded text-right focus:ring-hyf-accent focus:border-hyf-accent" />
                </div>
            </td>
            <td class="px-4 py-3 whitespace-nowrap text-right font-semibold subtotal">$0</td>
            <td class="px-4 py-3 whitespace-nowrap text-center">
                <button type="button" class="remove-row text-hyf-danger hover:text-red-800">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        `;
        serviciosTbody.appendChild(nuevaFila);
    });

    // Eliminar servicio (fila)
    serviciosTbody.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-row')) {
            const fila = e.target.closest('tr');
            fila.remove();

            // Si no quedan filas, mostrar mensaje "No hay servicios"
            if (serviciosTbody.children.length === 0) {
                const noServicios = document.createElement('tr');
                noServicios.id = 'no-servicios-row';
                noServicios.innerHTML = `<td colspan="5" class="px-5 py-5 text-center text-gray-500 italic select-none">No hay servicios o productos asociados.</td>`;
                serviciosTbody.appendChild(noServicios);
            }
        }
    });
});
