% ==================================
% DECLARACIONES DINAMICAS
% ==================================

:- dynamic enfermedad/1.
:- dynamic descripcion/2.
:- dynamic sintoma/2.
:- dynamic clasificacion/2.
:- dynamic contraindicado/2.
:- dynamic trata/2.

% ==================================
% REGLAS UNIVERSALES
% ==================================

coincidencias(E, Lista, Cantidad) :-
    findall(S,
        (member(S, Lista), sintoma(E, S)),
        L),
    length(L, Cantidad).

total_sintomas(E, Total) :-
    findall(S, sintoma(E, S), L),
    length(L, Total).

afinidad(E, Lista, Porcentaje) :-
    coincidencias(E, Lista, C),
    total_sintomas(E, T),
    T > 0,
    Porcentaje is (C / T) * 100.

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

nivel_urgencia(_, P, 'Baja') :-
    P < 40.

medicamento_seguro(E, M) :-
    trata(M, E),
    \+ contraindicado(E, M).

explicacion(E, Lista, Coinciden) :-
    findall(S,
        (member(S, Lista), sintoma(E, S)),
        Coinciden).

diagnostico(ListaSintomas, E, P, Urgencia) :-
    enfermedad(E),
    afinidad(E, ListaSintomas, P),
    P >= 30,
    nivel_urgencia(E, P, Urgencia).

enfermedad(gripe).
descripcion(gripe,'Infección viral aguda del sistema respiratorio').
sintoma(gripe,fiebre).
sintoma(gripe,tos).
sintoma(gripe,dolor_muscular).
sintoma(gripe,congestión_nasal).
contraindicado(gripe,antibioticos).
contraindicado(gripe,corticoides_sin_indicacion).
clasificacion(gripe,respiratorio).
clasificacion(gripe,viral).
clasificacion(gripe,agudo).
enfermedad(asma).
descripcion(asma,'Enfermedad crónica que inflama y estrecha las vías respiratorias').
sintoma(asma,dificultad_respiratoria).
sintoma(asma,sibilancias).
sintoma(asma,tos).
sintoma(asma,opresion_toracica).
contraindicado(asma,aspirina).
contraindicado(asma,betabloqueadores).
clasificacion(asma,respiratorio).
clasificacion(asma,cronico).
enfermedad(diabetes_tipo_2).
descripcion(diabetes_tipo_2,'Trastorno metabólico caracterizado por hiperglucemia').
sintoma(diabetes_tipo_2,sed_excesiva).
sintoma(diabetes_tipo_2,orinar_frecuente).
sintoma(diabetes_tipo_2,fatiga).
sintoma(diabetes_tipo_2,vision_borrosa).
contraindicado(diabetes_tipo_2,corticoides).
contraindicado(diabetes_tipo_2,diureticos_tiazidicos).
clasificacion(diabetes_tipo_2,endocrino).
clasificacion(diabetes_tipo_2,cronico).
enfermedad(gastritis).
descripcion(gastritis,'Inflamación de la mucosa del estómago').
sintoma(gastritis,dolor_abdominal).
sintoma(gastritis,nauseas).
sintoma(gastritis,acidez).
sintoma(gastritis,vomitos).
contraindicado(gastritis,antiinflamatorios_no_esteroideos).
clasificacion(gastritis,digestivo).
enfermedad(hipertensión_arterial).
descripcion(hipertensión_arterial,'Elevación persistente de la presión arterial').
sintoma(hipertensión_arterial,dolor_de_cabeza).
sintoma(hipertensión_arterial,mareos).
sintoma(hipertensión_arterial,vision_borrosa).
contraindicado(hipertensión_arterial,descongestionantes).
contraindicado(hipertensión_arterial,antiinflamatorios).
clasificacion(hipertensión_arterial,cardiovascular).
clasificacion(hipertensión_arterial,cronico).
enfermedad(covid-19).
descripcion(covid-19,'Enfermedad infecciosa causada por un coronavirus').
sintoma(covid-19,fiebre).
sintoma(covid-19,tos_seca).
sintoma(covid-19,perdida_del_olfato).
sintoma(covid-19,dificultad_respiratoria).
contraindicado(covid-19,automedicacion_con_antibioticos).
clasificacion(covid-19,respiratorio).
clasificacion(covid-19,viral).
enfermedad(tuberculosis).
descripcion(tuberculosis,'Infección bacteriana que afecta principalmente los pulmones').
sintoma(tuberculosis,tos_cronica).
sintoma(tuberculosis,fiebre).
sintoma(tuberculosis,sudoracion_nocturna).
sintoma(tuberculosis,perdida_de_peso).
contraindicado(tuberculosis,corticoides_sin_supervision).
clasificacion(tuberculosis,respiratorio).
clasificacion(tuberculosis,infeccioso).
enfermedad(hepatitis_b).
descripcion(hepatitis_b,'Infección viral que afecta el hígado').
sintoma(hepatitis_b,ictericia).
sintoma(hepatitis_b,fatiga).
sintoma(hepatitis_b,dolor_abdominal).
sintoma(hepatitis_b,nauseas).
contraindicado(hepatitis_b,alcohol).
contraindicado(hepatitis_b,paracetamol_en_exceso).
clasificacion(hepatitis_b,digestivo).
clasificacion(hepatitis_b,viral).
enfermedad(anemia_ferropénica).
descripcion(anemia_ferropénica,'Disminución de glóbulos rojos por falta de hierro').
sintoma(anemia_ferropénica,fatiga).
sintoma(anemia_ferropénica,palidez).
sintoma(anemia_ferropénica,mareos).
sintoma(anemia_ferropénica,taquicardia).
contraindicado(anemia_ferropénica,antiacidos).
contraindicado(anemia_ferropénica,quelantes_de_hierro).
clasificacion(anemia_ferropénica,hematologico).
enfermedad(artritis_reumatoide).
descripcion(artritis_reumatoide,'Enfermedad autoinmune que inflama las articulaciones').
sintoma(artritis_reumatoide,dolor_articular).
sintoma(artritis_reumatoide,rigidez_matutina).
sintoma(artritis_reumatoide,hinchazon).
contraindicado(artritis_reumatoide,antiinflamatorios_prolongados_sin_control).
clasificacion(artritis_reumatoide,inmunologico).
clasificacion(artritis_reumatoide,cronico).
enfermedad(migraña).
descripcion(migraña,'Trastorno neurológico caracterizado por dolor de cabeza intenso').
sintoma(migraña,dolor_pulsante).
sintoma(migraña,nauseas).
sintoma(migraña,fotofobia).
contraindicado(migraña,vasodilatadores).
clasificacion(migraña,neurologico).
enfermedad(hipotiroidismo).
descripcion(hipotiroidismo,'Producción insuficiente de hormonas tiroideas').
sintoma(hipotiroidismo,aumento_de_peso).
sintoma(hipotiroidismo,fatiga).
sintoma(hipotiroidismo,intolerancia_al_frio).
contraindicado(hipotiroidismo,litio).
contraindicado(hipotiroidismo,amiodarona).
clasificacion(hipotiroidismo,endocrino).
clasificacion(hipotiroidismo,cronico).
enfermedad(dengue).
descripcion(dengue,'Infección viral transmitida por mosquitos').
sintoma(dengue,fiebre_alta).
sintoma(dengue,dolor_muscular).
sintoma(dengue,dolor_ocular).
sintoma(dengue,sangrado).
contraindicado(dengue,aspirina).
contraindicado(dengue,ibuprofeno).
clasificacion(dengue,viral).
clasificacion(dengue,infeccioso).
enfermedad(colitis).
descripcion(colitis,'Inflamación del colon').
sintoma(colitis,diarrea).
sintoma(colitis,dolor_abdominal).
sintoma(colitis,distension).
contraindicado(colitis,antibioticos_innecesarios).
clasificacion(colitis,digestivo).
enfermedad(insuficiencia_renal_crónica).
descripcion(insuficiencia_renal_crónica,'Pérdida progresiva de la función renal').
sintoma(insuficiencia_renal_crónica,fatiga).
sintoma(insuficiencia_renal_crónica,edema).
sintoma(insuficiencia_renal_crónica,nauseas).
contraindicado(insuficiencia_renal_crónica,antiinflamatorios_no_esteroideos).
clasificacion(insuficiencia_renal_crónica,renal).
clasificacion(insuficiencia_renal_crónica,cronico).
enfermedad(epilepsia).
descripcion(epilepsia,'Trastorno neurológico caracterizado por convulsiones recurrentes').
sintoma(epilepsia,convulsiones).
sintoma(epilepsia,perdida_de_conciencia).
sintoma(epilepsia,confusion).
contraindicado(epilepsia,alcohol).
contraindicado(epilepsia,antidepresivos_especificos).
clasificacion(epilepsia,neurologico).
clasificacion(epilepsia,cronico).
enfermedad(neumonía).
descripcion(neumonía,'Infección que inflama los sacos aéreos de los pulmones').
sintoma(neumonía,fiebre).
sintoma(neumonía,tos_con_flema).
sintoma(neumonía,dolor_toracico).
contraindicado(neumonía,antitusivos_sin_indicacion).
clasificacion(neumonía,respiratorio).
clasificacion(neumonía,infeccioso).
enfermedad(psoriasis).
descripcion(psoriasis,'Enfermedad inflamatoria crónica de la piel').
sintoma(psoriasis,placas_rojas).
sintoma(psoriasis,descamacion).
sintoma(psoriasis,picazon).
contraindicado(psoriasis,corticoides_sistemicos_sin_control).
clasificacion(psoriasis,dermatologico).
clasificacion(psoriasis,inmunologico).
enfermedad(reflujo_gastroesofágico).
descripcion(reflujo_gastroesofágico,'Paso del contenido gástrico al esófago').
sintoma(reflujo_gastroesofágico,acidez).
sintoma(reflujo_gastroesofágico,regurgitacion).
sintoma(reflujo_gastroesofágico,dolor_toracico).
contraindicado(reflujo_gastroesofágico,antiinflamatorios).
contraindicado(reflujo_gastroesofágico,alcohol).
clasificacion(reflujo_gastroesofágico,digestivo).
clasificacion(reflujo_gastroesofágico,cronico).
enfermedad(lupus).
descripcion(lupus,'Enfermedad autoinmune sistémica').
sintoma(lupus,fatiga).
sintoma(lupus,dolor_articular).
sintoma(lupus,erupciones_cutaneas).
contraindicado(lupus,exposicion_solar_excesiva).
clasificacion(lupus,inmunologico).
clasificacion(lupus,cronico).
enfermedad(bronquitis).
descripcion(bronquitis,'Inflamación de los bronquios').
sintoma(bronquitis,tos_persistente).
sintoma(bronquitis,flema).
sintoma(bronquitis,dolor_toracico).
contraindicado(bronquitis,antibioticos_innecesarios).
clasificacion(bronquitis,respiratorio).
enfermedad(varicela).
descripcion(varicela,'Infección viral altamente contagiosa').
sintoma(varicela,fiebre).
sintoma(varicela,erupcion_cutanea).
sintoma(varicela,picazon).
contraindicado(varicela,aspirina).
clasificacion(varicela,viral).
clasificacion(varicela,infeccioso).
enfermedad(obesidad).
descripcion(obesidad,'Acumulación excesiva de grasa corporal').
sintoma(obesidad,aumento_de_peso).
sintoma(obesidad,fatiga).
sintoma(obesidad,dolor_articular).
contraindicado(obesidad,supresores_del_apetito_sin_control).
clasificacion(obesidad,endocrino).
clasificacion(obesidad,cronico).
enfermedad(insomnio).
descripcion(insomnio,'Trastorno del sueño').
sintoma(insomnio,dificultad_para_dormir).
sintoma(insomnio,irritabilidad).
sintoma(insomnio,fatiga).
contraindicado(insomnio,estimulantes).
clasificacion(insomnio,neurologico).
enfermedad(cistitis).
descripcion(cistitis,'Inflamación de la vejiga').
sintoma(cistitis,ardor_al_orinar).
sintoma(cistitis,dolor_abdominal).
sintoma(cistitis,orina_turbia).
contraindicado(cistitis,automedicacion_antibiotica).
clasificacion(cistitis,urinario).
clasificacion(cistitis,infeccioso).
enfermedad(sinusitis).
descripcion(sinusitis,'Inflamación de los senos paranasales').
sintoma(sinusitis,dolor_facial).
sintoma(sinusitis,congestion_nasal).
sintoma(sinusitis,secrecion).
contraindicado(sinusitis,descongestionantes_prolongados).
clasificacion(sinusitis,respiratorio).
enfermedad(osteoporosis).
descripcion(osteoporosis,'Disminución de la densidad ósea').
sintoma(osteoporosis,fracturas).
sintoma(osteoporosis,dolor_oseo).
sintoma(osteoporosis,perdida_de_estatura).
contraindicado(osteoporosis,corticoides_prolongados).
clasificacion(osteoporosis,oseo).
clasificacion(osteoporosis,cronico).
enfermedad(ansiedad).
descripcion(ansiedad,'Trastorno emocional').
sintoma(ansiedad,nerviosismo).
sintoma(ansiedad,taquicardia).
sintoma(ansiedad,insomnio).
contraindicado(ansiedad,benzodiacepinas_sin_control).
clasificacion(ansiedad,psicologico).
enfermedad(parkinson).
descripcion(parkinson,'Enfermedad neurodegenerativa progresiva').
sintoma(parkinson,temblores).
sintoma(parkinson,rigidez).
sintoma(parkinson,lentitud_de_movimiento).
contraindicado(parkinson,antipsicoticos_tipicos).
clasificacion(parkinson,neurologico).
clasificacion(parkinson,cronico).
enfermedad(alzheimer).
descripcion(alzheimer,'Trastorno neurodegenerativo progresivo').
sintoma(alzheimer,perdida_de_memoria).
sintoma(alzheimer,confusion).
sintoma(alzheimer,desorientacion).
contraindicado(alzheimer,sedantes_innecesarios).
clasificacion(alzheimer,neurologico).
clasificacion(alzheimer,cronico).
