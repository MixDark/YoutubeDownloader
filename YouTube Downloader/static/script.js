let rutaArchivoDescargado = ''; // Variable para almacenar la ruta del archivo descargado

// Añado un evento para mostrar/ocultar el selector de calidad según el formato
document.getElementById('format').addEventListener('change', function() {
    const qualitySelect = document.getElementById('quality');
    qualitySelect.style.display = this.value === 'mp4' ? 'inline' : 'none';
});

// Función para mostrar detalles del video
function mostrarDetallesVideo(data) {
    document.getElementById('thumbnail').src = data.thumbnail;
    document.getElementById('video-title').innerText = data.title;
    document.getElementById('video-channel').innerText = `Canal: ${data.channel}`;
    document.getElementById('video-duration').innerText = `Duración: ${data.duration}`;
    document.getElementById('video-details').style.display = 'block';
}

// Función para obtener la información del video
function fetchVideoInfo() {
    const url = document.getElementById('url').value;
    if (!url) {
        document.getElementById('video-details').style.display = 'none';
        return;
    }

    fetch(`/get_video_info?url=${encodeURIComponent(url)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('status').innerHTML = 'Error al obtener detalles del video: ' + data.error;
                console.error('Error:', data.error);
                document.getElementById('video-details').style.display = 'none';
            } else {
                mostrarDetallesVideo(data);
            }
        })
        .catch(error => {
            document.getElementById('status').innerHTML = 'Error al obtener los detalles del video: ' + error.message;
            console.error('Error:', error);
            document.getElementById('video-details').style.display = 'none';
        });
}

// Función para actualizar la barra de progreso
function actualizarProgreso(porcentaje) {
    const barra = document.getElementById('progress');
    barra.style.width = porcentaje + '%';
    barra.innerText = porcentaje + '%'; // Mostrar el porcentaje dentro de la barra
}

// Función para abrir la ubicación del archivo descargado
function abrirUbicacion() {
    if (rutaArchivoDescargado) {
        // Enviar una solicitud al servidor para abrir la ubicación del archivo
        fetch(`/abrir_ubicacion?ruta=${encodeURIComponent(rutaArchivoDescargado)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Ubicación abierta correctamente');
                } else {
                    console.error('Error al abrir la ubicación:', data.error);
                }
            })
            .catch(error => {
                console.error('Error al abrir la ubicación:', error);
            });
    } else {
        console.error('No se ha descargado ningún archivo.');
    }
}

// Mi función principal para manejar las descargas
function descargar() {
    // Obtengo los valores de los campos del formulario
    const url = document.getElementById('url').value;
    const format = document.getElementById('format').value;
    const quality = document.getElementById('quality').value;
    const status = document.getElementById('status');

    // Verifico que se haya ingresado una URL
    if (!url) {
        status.innerHTML = 'Por favor, ingresa una URL de YouTube';
        return;
    }

    // Actualizo el estado para mostrar que la descarga está en proceso
    status.innerHTML = 'Descargando...';
    actualizarProgreso(0); // Reinicio la barra de progreso
    document.getElementById('progress-container').style.display = 'block';
    document.getElementById('abrir-ubicacion').style.display = 'none'; // Ocultar el botón de abrir ubicación

    // Realizo la petición al servidor para iniciar la descarga
    fetch(`/descargar?url=${encodeURIComponent(url)}&format=${format}&quality=${quality}`)
        .then(response => {
            const reader = response.body.getReader();
            const contentLength = +response.headers.get('Content-Length');

            let recibido = 0;
            return reader.read().then(function procesar({ done, value }) {
                if (done) {
                    status.innerHTML = 'Descarga completada.';
                    document.getElementById('abrir-ubicacion').style.display = 'inline-block'; // Mostrar el botón de abrir ubicación
                    return;
                }

                recibido += value.length;
                const porcentaje = Math.round((recibido / contentLength) * 100);
                actualizarProgreso(porcentaje);

                return reader.read().then(procesar);
            });
        })
        .then(() => {
            // Obtener la ruta del archivo descargado
            fetch(`/obtener_ruta_descarga?url=${encodeURIComponent(url)}&format=${format}&quality=${quality}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        rutaArchivoDescargado = data.file; // Guardar la ruta del archivo descargado
                    }
                })
                .catch(error => {
                    console.error('Error al obtener la ruta del archivo:', error);
                });
        })
        .catch(error => {
            status.innerHTML = 'Error en la descarga: ' + error.message;
            console.error('Error:', error);
            document.getElementById('progress-container').style.display = 'none';
        });
}