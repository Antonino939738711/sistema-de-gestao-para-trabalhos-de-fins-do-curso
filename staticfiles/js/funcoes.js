// Funções genéricas de abrir/fechar modais
function abrirModal(id) {
  document.getElementById(id).classList.remove('hidden');
  document.getElementById(id).classList.add('flex');
}
function fecharModal(id) {
  document.getElementById(id).classList.remove('flex');
  document.getElementById(id).classList.add('hidden');
}

// Botões de abrir
document.getElementById('btnAddPacientes')?.addEventListener('click', () => abrirModal('modalAddPacientes'));

// Botões de fechar
document.getElementById('closeAddPacientes')?.addEventListener('click', () => fecharModal('modalAddPacientes'));
document.getElementById('closeUpdatePacientes')?.addEventListener('click', () => fecharModal('modalUpdatePacientes'));
document.getElementById('closeModalReceita')?.addEventListener('click', () => fecharModal('modalReceita'));

// Abertura dinâmica do modal de atualização
function abrirModalUpdate(id) {
  const modal = document.getElementById('modalUpdatePacientes');
  modal.querySelector('form').action = `/atualizar_paciente/${id}/`;
  abrirModal('modalUpdatePacientes');
}
