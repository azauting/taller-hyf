document.addEventListener('DOMContentLoaded', () => {
    // Buscador de clientes
    $('#buscador-cliente').on('input', async function () {
        const query = $(this).val().trim();
        if (query.length < 2) {
            $('#resultados-cliente').empty().hide();
            return;
        }

        try {
            const response = await fetch(`/panel/cliente/buscar?q=${encodeURIComponent(query)}`);


            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }

            const data = await response.json();
            const resultados = $('#resultados-cliente');
            resultados.empty();

            if (data.length === 0) {
                resultados.append('<div class="p-3 text-gray-500">No se encontraron clientes</div>');
            } else {
                data.forEach(cliente => {
                    const item = $(`
                        <div class="p-3 hover:bg-gray-100 cursor-pointer border-b border-gray-100 cliente-item" 
                             data-id="${cliente.id}" 
                             data-nombre="${cliente.nombre} ${cliente.apellido}"
                             data-telefono="${cliente.telefono}">
                            <p class="font-medium">${cliente.nombre} ${cliente.apellido}</p>
                            <p class="text-sm text-gray-600">${cliente.telefono}</p>
                        </div>
                    `);
                    resultados.append(item);
                });
            }

            resultados.show();
        } catch (error) {
            console.error('Error al buscar clientes:', error);
            $('#resultados-cliente').empty().append('<div class="p-3 text-red-500">Error al buscar clientes</div>').show();
        }
    });

    // Seleccionar cliente
    $(document).on('click', '.cliente-item', function () {
        const id = $(this).data('id');
        const nombre = $(this).data('nombre');
        const telefono = $(this).data('telefono');

        $('#cliente-id').val(id);
        $('#cliente-nombre').text(nombre);
        $('#cliente-telefono').text(telefono);
        $('#info-cliente').show();
        $('#buscador-cliente').val('').hide();
        $('#resultados-cliente').empty().hide();

        // Cargar vehículos del cliente seleccionado
        cargarVehiculosCliente(id);
    });

    // Cambiar cliente
    $('#cambiar-cliente').click(function () {
        $('#cliente-id').val('');
        $('#info-cliente').hide();
        $('#buscador-cliente').val('').show();
        $('#vehiculo-select').html('<option value="">-- Selecciona un vehículo --</option>');
    });

    // Ocultar resultados al hacer clic fuera
    $(document).click(function (e) {
        if (!$(e.target).closest('#buscador-cliente, #resultados-cliente').length) {
            $('#resultados-cliente').hide();
        }
    });
},)
