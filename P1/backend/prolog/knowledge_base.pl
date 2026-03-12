% ==================================
% DECLARACIONES DINAMICAS
% ==================================

:- dynamic enfermedad/1.
:- dynamic descripcion/2.
:- dynamic sintoma/2.
:- dynamic clasificacion/2.
:- dynamic contraindicado/2.
:- dynamic trata/2.
:- dynamic medicamento/2.          % medicamento(Nombre, Descripcion)
:- dynamic alternativa/2.          % alternativa(MedicamentoConflicto, MedicamentoAlternativo)

% ==================================
% REGLAS UNIVERSALES — DIAGNÓSTICO
% ==================================

coincidencias(E, Lista, Cantidad) :-
    findall(S,
        (member(S, Lista), sintoma(E, S)),
        L),
    length(L, Cantidad).

total_sintomas(E, Total) :-alcohol, medicamentos-hepatotoxicos  
    findall(S, sintoma(E, S), L),
    length(L, Total).

% ── Afinidad base (sin severidad) ──────────────────────────────────────
afinidad(E, Lista, Porcentaje) :-
    coincidencias(E, Lista, C),
    total_sintomas(E, T),
    T > 0,
    Porcentaje is round((C / T) * 100).

% ── Afinidad ponderada por severidad ───────────────────────────────────
% Recibe lista de pares sintoma-nivel: [[fiebre,severo],[tos,leve],...]
% leve=0.5 | moderado=1.0 | severo=1.5
peso_severidad(leve,     0.5).
peso_severidad(moderado, 1.0).
peso_severidad(severo,   1.5).

% Suma los pesos de síntomas que coinciden con la enfermedad
suma_pesos_coincidentes(_, [], 0).
suma_pesos_coincidentes(E, [[S, Nivel]|Resto], Total) :-
    (sintoma(E, S) ->
        peso_severidad(Nivel, P),
        suma_pesos_coincidentes(E, Resto, SubTotal),
        Total is SubTotal + P
    ;
        suma_pesos_coincidentes(E, Resto, Total)
    ).

% Peso máximo posible = cada síntoma de la enfermedad con peso 1.5
peso_maximo(E, Max) :-
    findall(S, sintoma(E, S), Sintomas),
    length(Sintomas, N),
    Max is N * 1.5.

afinidad_ponderada(E, ListaPares, Porcentaje) :-
    suma_pesos_coincidentes(E, ListaPares, Suma),
    peso_maximo(E, Max),
    Max > 0,
    Suma > 0,
    Porcentaje is round((Suma / Max) * 100).

% ==================================
% REGLAS UNIVERSALES — URGENCIA
% ==================================

nivel_urgencia(E, P, 'Alta') :-
    clasificacion(E, cronico),
    P >= 60, !.

nivel_urgencia(E, P, 'Alta') :-
    clasificacion(E, infeccioso),
    P >= 70, !.

nivel_urgencia(_, P, 'Alta') :-
    P >= 70, !.

nivel_urgencia(_, P, 'Media') :-
    P >= 40,
    P < 70, !.

nivel_urgencia(_, _, 'Baja').

% Etiqueta de acción según urgencia
accion_urgencia('Alta',  'Consulta médica inmediata sugerida').
accion_urgencia('Media', 'Observación recomendada').
accion_urgencia('Baja',  'Posible automanejo').

% ==================================
% REGLAS UNIVERSALES — MEDICAMENTOS
% ==================================

% Medicamento seguro: trata la enfermedad y no está contraindicado
medicamento_seguro(E, M) :-
    trata(M, E),
    \+ contraindicado(E, M).

% Obtiene el primer medicamento seguro disponible
primer_medicamento_seguro(E, M) :-
    medicamento_seguro(E, M), !.

% Si no hay medicamento seguro, devuelve 'ninguno'
primer_medicamento_seguro(_, ninguno).

% Lista todos los medicamentos seguros para una enfermedad
todos_medicamentos_seguros(E, Lista) :-
    findall(M, medicamento_seguro(E, M), Lista).

% ==================================
% REGLAS UNIVERSALES — EXPLICACIÓN
% ==================================

% Qué síntomas del paciente coincidieron con la enfermedad
explicacion(E, Lista, Coinciden) :-
    findall(S,
        (member(S, Lista), sintoma(E, S)),
        Coinciden).

% Qué síntomas de la enfermedad NO reportó el paciente (síntomas ausentes)
sintomas_ausentes(E, Lista, Ausentes) :-
    findall(S,
        (sintoma(E, S), \+ member(S, Lista)),
        Ausentes).

% ==================================
% CONSULTA PRINCIPAL — DIAGNÓSTICO
% ==================================

% ==================================
% Diagnóstico base (sin severidad)
% ==================================
diagnostico(ListaSintomas, E, P, Urgencia) :-
    enfermedad(E),
    afinidad(E, ListaSintomas, P),
    P >= 30,
    nivel_urgencia(E, P, Urgencia).

% ==================================
% Diagnóstico ponderado (con severidad)
% ==================================
% ListaPares = [[sintoma, nivel_severidad], ...]
diagnostico_ponderado(ListaPares, E, P, Urgencia) :-
    enfermedad(E),
    afinidad_ponderada(E, ListaPares, P),
    P >= 30,
    nivel_urgencia(E, P, Urgencia).

% ==================================
% Diagnóstico completo con medicamento seguro
% ==================================
diagnostico_completo(ListaSintomas, E, P, Urgencia, Accion, Medicamento, Coinciden) :-
    diagnostico(ListaSintomas, E, P, Urgencia),
    accion_urgencia(Urgencia, Accion),
    primer_medicamento_seguro(E, Medicamento),
    explicacion(E, ListaSintomas, Coinciden).

% ==================================
% Diagnóstico completo ponderado
% ==================================
diagnostico_completo_ponderado(ListaPares, E, P, Urgencia, Accion, Medicamento, Coinciden) :-
    diagnostico_ponderado(ListaPares, E, P, Urgencia),
    accion_urgencia(Urgencia, Accion),
    primer_medicamento_seguro(E, Medicamento),
    findall(S, (member([S,_], ListaPares), sintoma(E, S)), Coinciden).












% ==================================
% ENFERMEDADES Y HECHOS — Generado automáticamente
% ==================================

enfermedad(neumonia_bacteriana).
descripcion(neumonia_bacteriana,'Infección pulmonar causada por bacterias que inflaman los alvéolos').
sintoma(neumonia_bacteriana,fiebre_alta).
sintoma(neumonia_bacteriana,tos_con_flema).
sintoma(neumonia_bacteriana,dificultad_respiratoria).
sintoma(neumonia_bacteriana,dolor_toracico).
sintoma(neumonia_bacteriana,escalofrios).
contraindicado(neumonia_bacteriana,ibuprofeno_sin_supervision).
contraindicado(neumonia_bacteriana,aspirina_en_ninos).
clasificacion(neumonia_bacteriana,respiratorio).
clasificacion(neumonia_bacteriana,infeccioso).
clasificacion(neumonia_bacteriana,agudo).
enfermedad(hepatitis_a).
descripcion(hepatitis_a,'Infección viral del hígado transmitida por agua o alimentos contaminados').
sintoma(hepatitis_a,ictericia).
sintoma(hepatitis_a,fatiga).
sintoma(hepatitis_a,nauseas).
sintoma(hepatitis_a,dolor_abdominal).
sintoma(hepatitis_a,fiebre).
sintoma(hepatitis_a,orina_oscura).
sintoma(hepatitis_a,orina_roja).
contraindicado(hepatitis_a,paracetamol_excesivo).
contraindicado(hepatitis_a,alcohol).
contraindicado(hepatitis_a,medicamentos_hepatotoxicos).
clasificacion(hepatitis_a,digestivo).
clasificacion(hepatitis_a,viral).
clasificacion(hepatitis_a,agudo).
clasificacion(hepatitis_a,infeccioso).
enfermedad(hipertiroidismo).
descripcion(hipertiroidismo,'Producción excesiva de hormonas tiroideas que acelera el metabolismo').
sintoma(hipertiroidismo,perdida_de_peso).
sintoma(hipertiroidismo,taquicardia).
sintoma(hipertiroidismo,temblores).
sintoma(hipertiroidismo,sudoracion_excesiva).
sintoma(hipertiroidismo,nerviosismo).
sintoma(hipertiroidismo,insomnio).
sintoma(hipertiroidismo,corazon_roto).
contraindicado(hipertiroidismo,estimulantes).
contraindicado(hipertiroidismo,cafeina_excesiva).
contraindicado(hipertiroidismo,gaseosa_excesiva).
contraindicado(hipertiroidismo,dolor_sumamente_excesivo).
clasificacion(hipertiroidismo,endocrino).
clasificacion(hipertiroidismo,cronico).

% TRATAMIENTOS — trata(Medicamento, Enfermedad)
trata(paracetamol,hepatitis_a).

% === RPA Carga automática — 2026-03-12 14:39:35 ===
enfermedad(neumonia_bacteriana).
descripcion(neumonia_bacteriana,'Infección pulmonar causada por bacterias que inflaman los alvéolos').
sintoma(neumonia_bacteriana,fiebre_alta).
sintoma(neumonia_bacteriana,tos_con_flema).
sintoma(neumonia_bacteriana,dificultad_respiratoria).
sintoma(neumonia_bacteriana,dolor_toracico).
sintoma(neumonia_bacteriana,escalofrios).
contraindicado(neumonia_bacteriana,ibuprofeno_sin_supervision).
contraindicado(neumonia_bacteriana,aspirina_en_ninos).
clasificacion(neumonia_bacteriana,respiratorio).
clasificacion(neumonia_bacteriana,infeccioso).
clasificacion(neumonia_bacteriana,agudo).
enfermedad(hepatitis_a).
descripcion(hepatitis_a,'Infección viral del hígado transmitida por agua o alimentos contaminados').
sintoma(hepatitis_a,ictericia).
sintoma(hepatitis_a,fatiga).
sintoma(hepatitis_a,nauseas).
sintoma(hepatitis_a,dolor_abdominal).
sintoma(hepatitis_a,fiebre).
sintoma(hepatitis_a,orina_oscura).
contraindicado(hepatitis_a,paracetamol_excesivo).
contraindicado(hepatitis_a,alcohol).
contraindicado(hepatitis_a,medicamentos_hepatotoxicos).
clasificacion(hepatitis_a,digestivo).
clasificacion(hepatitis_a,viral).
clasificacion(hepatitis_a,agudo).
clasificacion(hepatitis_a,infeccioso).
enfermedad(hipertiroidismo).
descripcion(hipertiroidismo,'Producción excesiva de hormonas tiroideas que acelera el metabolismo').
sintoma(hipertiroidismo,perdida_de_peso).
sintoma(hipertiroidismo,taquicardia).
sintoma(hipertiroidismo,temblores).
sintoma(hipertiroidismo,sudoracion_excesiva).
sintoma(hipertiroidismo,nerviosismo).
sintoma(hipertiroidismo,insomnio).
contraindicado(hipertiroidismo,estimulantes).
contraindicado(hipertiroidismo,cafeina_excesiva).
contraindicado(hipertiroidismo,yodo_sin_supervision).
clasificacion(hipertiroidismo,endocrino).
clasificacion(hipertiroidismo,cronico).