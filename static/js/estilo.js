
// Alerta simples com ícone
function mostrarAlerta() {
    Swal.fire({
        icon: 'info',               // Ícones: info, success, error, warning, question
        title: 'Aviso',
        text: 'Esta é uma mensagem de alerta simples!'
    });
}

// Alerta com confirmação (OK e Cancelar)
function confirmarAcao() {
    Swal.fire({
        title: 'Tem certeza?',
        text: 'Você deseja continuar com essa ação?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sim, continuar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({
                icon: 'success',
                title: 'Confirmado!',
                text: 'Você clicou em OK.'
            });
        } else if (result.dismiss === Swal.DismissReason.cancel) {
            Swal.fire({
                icon: 'error',
                title: 'Cancelado',
                text: 'Você clicou em Cancelar.'
            });
        }
    });
}