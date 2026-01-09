    const togglePwd = document.getElementById("togglePwd");
    const senhaInput = document.getElementById("senha");
    const iconEye = document.getElementById("iconEye");

    togglePwd.addEventListener("click", () => {
    
      if (senhaInput.type === "password") {
         iconEye.src = "{% static 'imgs/eye.png' %}"; 
         senhaInput.type = "text";
        iconEye.alt = "Ocultar senha";
        
       
      }else{
        senhaInput.type = "password";
       iconEye.src = "{%  static 'imgs/eye-off.png' %}";
        iconEye.alt = "Mostrar senha";
      }
    });

   
    const perfilSelect = document.getElementById("perfil");
    const camposMedico = document.getElementById("camposMedico");

    perfilSelect.addEventListener("change", () => {
      if (perfilSelect.value === "medico") {
        camposMedico.classList.remove("hidden");
      } else {
        camposMedico.classList.add("hidden");
      }
    });