document.addEventListener('DOMContentLoaded', () => {
    // crear cliente

    // Crear nuevo cliente vía AJAX
    $('#crear-cliente').click(() => {
        const nombre = $('#nuevo-nombre').val().trim();
        const apellido = $('#nuevo-apellido').val().trim();
        const telefono = $('#nuevo-telefono').val().trim();

        if (!nombre || !apellido || !telefono) {
            alert('Por favor, completa todos los campos del cliente.');
            return;
        }

        const data = new FormData();
        data.append('nombre', nombre);
        data.append('apellido', apellido);
        data.append('telefono', telefono);

        fetch('/cliente/ajax-crear', {
            method: 'POST',
            body: data
        })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json().then(data => {
                        // Actualizar campos del cliente seleccionado
                        $('#cliente-id').val(data.id);
                        $('#cliente-nombre').text(`${data.nombre} ${data.apellido}`);
                        $('#cliente-telefono').text(data.telefono);
                        $('#info-cliente').show();

                        // Ocultar el formulario de nuevo cliente
                        $('#form-nuevo-cliente').addClass('hidden');

                        // Limpiar inputs
                        $('#nuevo-nombre').val('');
                        $('#nuevo-apellido').val('');
                        $('#nuevo-telefono').val('');

                        alert('Cliente registrado con éxito.');

                        // Cargar vehículos del nuevo cliente (puede estar vacío)
                        cargarVehiculosCliente(data.id);
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al registrar cliente.');
            });
    });
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

    // Función para cargar vehículos del cliente
    function cargarVehiculosCliente(clienteId) {
        const vehiculoSelect = $('#vehiculo-select');
        vehiculoSelect.html('<option value="">-- Cargando vehículos... --</option>');
        vehiculoSelect.prop('disabled', true);

        if (!clienteId) {
            vehiculoSelect.html('<option value="">-- Selecciona un vehículo --</option>');
            vehiculoSelect.prop('disabled', false);
            return;
        }

        // Usando la nueva ruta que definimos
        fetch(`/panel/ticket_servicio/vehiculos-cliente/${clienteId}`)
            .then(res => {
                if (!res.ok) throw new Error('Error en la respuesta');
                return res.json();
            })
            .then(vehiculos => {
                vehiculoSelect.empty();

                if (vehiculos && vehiculos.length > 0) {
                    vehiculoSelect.append('<option value="">-- Selecciona un vehículo --</option>');
                    vehiculos.forEach(v => {
                        vehiculoSelect.append(
                            `<option value="${v.id}">${v.marca} ${v.modelo} - ${v.patente}</option>`
                        );
                    });
                } else {
                    vehiculoSelect.append('<option value="">No hay vehículos registrados</option>');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                vehiculoSelect.html('<option value="">Error cargando vehículos</option>');
            })
            .finally(() => {
                vehiculoSelect.prop('disabled', false);
            });
    }

    // Mostrar/ocultar formulario nuevo cliente
    $('#mostrar-form-cliente').click(() => {
        $('#form-nuevo-cliente').toggleClass('hidden');
    });

    // Cerrar formulario nuevo cliente
    $('#cerrar-form-cliente').click(() => {
        $('#form-nuevo-cliente').addClass('hidden');
    });

    // Mostrar/ocultar formulario nuevo vehículo
    $('#mostrar-form-vehiculo').click(() => {
        const clienteId = $('#cliente-id').val();
        if (!clienteId) {
            alert('Por favor, selecciona un cliente primero.');
            return;
        }
        $('#form-nuevo-vehiculo').toggleClass('hidden');
    });

    // Cerrar formulario nuevo vehículo
    $('#cerrar-form-vehiculo').click(() => {
        $('#form-nuevo-vehiculo').addClass('hidden');
    });

    // Crear vehículo nuevo vía AJAX
    $('#crear-vehiculo').click(() => {
        const clienteId = $('#cliente-id').val();
        const marca = $('#marca').val().trim();
        const modelo = $('#modelo').val().trim();
        const patente = $('#patente').val().trim();

        if (!clienteId) {
            alert('Por favor, selecciona un cliente primero.');
            return;
        }

        if (!marca || !modelo || !patente) {
            alert('Por favor, completa todos los campos del vehículo.');
            return;
        }

        const data = new FormData();
        data.append('cliente_id', clienteId);
        data.append('marca', marca);
        data.append('modelo', modelo);
        data.append('patente', patente);

        fetch('/vehiculo/crear', {
            method: 'POST',
            body: data
        })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json().then(data => {
                        // Añadir nuevo vehículo y seleccionarlo
                        $('#vehiculo-select').append(
                            `<option value="${data.id}" selected>${data.marca} ${data.modelo} - ${data.patente}</option>`
                        );
                        alert('Vehículo registrado con éxito.');
                        $('#form-nuevo-vehiculo').addClass('hidden');

                        // Limpiar inputs
                        $('#marca').val('');
                        $('#modelo').val('');
                        $('#patente').val('');
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al registrar vehículo.');
            });
    });

    // Manejo de servicios
    const serviciosTbody = $('#servicios-tbody');
    const noServiciosRow = $('#no-servicios-row');

    // Agregar nuevo servicio
    $('#add-servicio').click(() => {
        if (noServiciosRow.length) noServiciosRow.remove();

        const nuevaFila = `
            <tr class="nuevo-servicio">
                <td class="px-4 py-3 whitespace-nowrap">
                    <select name="tipo[]" class="w-full p-2 border border-gray-300 rounded focus:ring-hyf-accent focus:border-hyf-accent">
                        <option value="Servicio">Servicio</option>
                        <option value="Producto">Producto</option>
                    </select>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                    <input type="text" name="descripcion[]" placeholder="Descripción" required
                        class="w-full p-2 border border-gray-300 rounded focus:ring-hyf-accent focus:border-hyf-accent">
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-center">
                    <input type="number" name="cantidad[]" placeholder="Cantidad" min="1" required
                        class="w-16 p-2 border border-gray-300 rounded text-center focus:ring-hyf-accent focus:border-hyf-accent">
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-right">
                    <div class="relative">
                        <span class="absolute left-3 top-2 text-gray-500">$</span>
                        <input type="number" name="precio_unitario[]" placeholder="0" min="0" step="0.01" required
                            class="w-full pl-8 pr-3 p-2 border border-gray-300 rounded text-right focus:ring-hyf-accent focus:border-hyf-accent">
                    </div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-right font-semibold">
                    $0
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-center">
                    <button type="button" class="remove-row text-hyf-danger hover:text-red-800">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            </tr>
        `;
        serviciosTbody.append(nuevaFila);
        calcularTotalTicket()
    });

    // Eliminar servicio
    serviciosTbody.on('click', '.remove-row', function () {
        $(this).closest('tr').remove();

        // Si no quedan filas, mostrar mensaje
        if (serviciosTbody.children().length === 0) {
            serviciosTbody.append(`
                <tr id="no-servicios-row">
                    <td colspan="5" class="px-5 py-5 text-center text-gray-500 italic select-none">
                        No hay servicios o productos asociados.
                    </td>
                </tr>
            `);
        }
    });

    function calcularTotalTicket() {
        let total = 0;
        $('#servicios-tbody tr').each(function () {
            const fila = $(this);
            const cantidad = parseFloat(fila.find('input[name="cantidad[]"]').val()) || 0;
            const precio = parseFloat(fila.find('input[name="precio_unitario[]"]').val()) || 0;
            total += cantidad * precio;
        });

        // Actualizar texto del total en la interfaz
        $('.text-2xl.font-bold').text(`$${total.toLocaleString('es-CL')} CLP`);
    }

    serviciosTbody.on('input', 'input[name="cantidad[]"], input[name="precio_unitario[]"]', function () {
        const fila = $(this).closest('tr');
        const cantidad = parseFloat(fila.find('input[name="cantidad[]"]').val()) || 0;
        const precio = parseFloat(fila.find('input[name="precio_unitario[]"]').val()) || 0;
        const total = cantidad * precio;

        fila.find('td:nth-child(5)').text(`$${total.toLocaleString('es-CL')}`);
        calcularTotalTicket();
    });

});