import streamlit as st
import math
import pandas as pd

def james_gear_synthesis(i_1H, K_2, m, Z_min=17, max_iterations=50):
    """Расчёт чисел зубьев для механизма Джеймса"""
    results = []
    valid_solutions = []
    
    Z1 = Z_min
    iteration = 1
    
    while iteration <= max_iterations:
        # Расчёт чисел зубьев
        Z2 = (i_1H - 2) / 2 * Z1
        Z3 = (i_1H - 1) * Z1
        
        # Проверка условия сборки
        assembly_condition = (Z1 + Z3) / K_2
        
        # Проверка целочисленности
        is_Z2_integer = abs(Z2 - round(Z2)) < 1e-10
        is_Z3_integer = abs(Z3 - round(Z3)) < 1e-10
        is_assembly_integer = abs(assembly_condition - round(assembly_condition)) < 1e-10
        
        # Проверка передаточного отношения
        i_check = 1 + Z3 / Z1
        i_match = abs(i_check - i_1H) < 0.001
        
        # Условие соседства
        sin_threshold = math.sin(math.radians(180 / K_2))
        neighbor_value = (Z2 + 2) / (Z1 + Z2)
        neighbor_condition = neighbor_value < sin_threshold
        
        # Условие сборки
        assembly_ok = is_assembly_integer
        
        # Данные для таблицы
        status = "Найдено" if (is_Z2_integer and is_Z3_integer and i_match and 
                              neighbor_condition and assembly_ok) else "Отклонено"
        
        results.append({
            "Итерация": iteration,
            "Z1": Z1,
            "Z2": round(Z2, 2),
            "Z3": round(Z3, 2),
            "Сборка": round(assembly_condition, 2),
            "i_1H проверка": round(i_check, 3),
            "Соседство": "✅" if neighbor_condition else "❌",
            "Сборка": "✅" if assembly_ok else "❌",
            "Статус": status
        })
        
        # Сохранение подходящего решения
        if status == "Найдено":
            Z2_int = round(Z2)
            Z3_int = round(Z3)
            assembly_int = round(assembly_condition)
            
            solution_exists = any(sol[0] == Z1 and sol[1] == Z2_int for sol in valid_solutions)
            if not solution_exists:
                valid_solutions.append((Z1, Z2_int, Z3_int, assembly_int))
        
        Z1 += 1
        iteration += 1
    
    return results, valid_solutions

def main():
    st.set_page_config(
        page_title="Механизм Джеймса - Расчёт Чисел Зубьев",
        page_icon="⚙️",
        layout="wide"
    )
    
    # Заголовок
    st.title("⚙️ Расчёт Чисел Зубьев для Механизма Джеймса")
    st.markdown("---")
    
    # Боковая панель - параметры
    with st.sidebar:
        st.header("🎛️ Введите параметры")
        
        i_1H = st.number_input(
            "Передаточное отношение (i_1H)",
            min_value=1.1,
            max_value=10.0,
            value=3.5,
            step=0.1,
            help="Передаточное отношение механизма"
        )
        
        K_2 = st.number_input(
            "Число сателлитов (K_2)",
            min_value=2,
            max_value=6,
            value=2,
            step=1,
            help="Количество сателлитных колёс"
        )
        
        m = st.number_input(
            "Модуль (m) [мм]",
            min_value=0.5,
            max_value=5.0,
            value=1.5,
            step=0.1,
            help="Модуль зубьев"
        )
        
        Z_min = st.number_input(
            "Минимальное число зубьев (Z_min)",
            min_value=10,
            max_value=50,
            value=17,
            step=1,
            help="Минимальное число зубьев солнечной шестерни"
        )
        
        max_iterations = st.number_input(
            "Максимум итераций",
            min_value=10,
            max_value=100,
            value=30,
            step=5,
            help="Максимальное количество поисковых итераций"
        )
        
        calculate_btn = st.button("🎯 Начать расчёт", type="primary")
    
    # Основное поле
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Введённые параметры")
        param_data = {
            "Параметр": ["Передаточное отношение (i_1H)", "Число сателлитов (K_2)", 
                        "Модуль (m)", "Минимальное число зубьев (Z_min)", "Максимум итераций"],
            "Значение": [i_1H, K_2, f"{m} мм", Z_min, max_iterations]
        }
        st.dataframe(param_data, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("ℹ️ Условия")
        st.info("""
        **Условия механизма Джеймса:**
        - Z2 и Z3 должны быть целыми числами
        - (Z1 + Z3)/K_2 должно быть целым числом
        - (Z2 + 2)/(Z1 + Z2) < sin(180°/K_2)
        - i_1H = 1 + Z3/Z1
        """)
    
    if calculate_btn:
        st.markdown("---")
        st.subheader("🔍 Процесс расчёта")
        
        # Прогресс бар
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Расчёт
        with st.spinner("Выполняется расчёт чисел зубьев..."):
            results, valid_solutions = james_gear_synthesis(i_1H, K_2, m, Z_min, max_iterations)
            progress_bar.progress(100)
            status_text.success("✅ Расчёт завершён!")
        
        # Таблица результатов
        st.subheader("📋 Результаты расчёта")
        
        if results:
            df = pd.DataFrame(results)
            
            # Отображение таблицы
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Соседство": st.column_config.TextColumn("Соседство"),
                    "Сборка": st.column_config.TextColumn("Сборка"),
                    "Статус": st.column_config.TextColumn("Статус")
                }
            )
            
            # Подходящие решения
            st.subheader("🎯 Найденные решения")
            
            if valid_solutions:
                solutions_data = []
                for i, (Z1, Z2, Z3, assembly) in enumerate(valid_solutions, 1):
                    i_check = 1 + Z3 / Z1
                    solutions_data.append({
                        "№": i,
                        "Z1": Z1,
                        "Z2": Z2,
                        "Z3": Z3,
                        "Параметр сборки": assembly,
                        "i_1H проверка": round(i_check, 3)
                    })
                
                solutions_df = pd.DataFrame(solutions_data)
                st.dataframe(solutions_df, use_container_width=True, hide_index=True)
                
                # Лучшее решение
                if valid_solutions:
                    best_Z1, best_Z2, best_Z3, best_assembly = valid_solutions[0]
                    
                    st.success("### ⭐ Лучшее решение")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Z1", best_Z1)
                    with col2:
                        st.metric("Z2", best_Z2)
                    with col3:
                        st.metric("Z3", best_Z3)
                    with col4:
                        st.metric("Параметр сборки", best_assembly)
                    
                    # Результаты проверки
                    st.subheader("🔍 Результаты проверки")
                    
                    # Передаточное отношение
                    i_check = 1 + best_Z3 / best_Z1
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info(f"**Передаточное отношение:** i_1H = 1 + Z3/Z1 = 1 + {best_Z3}/{best_Z1} = {i_check:.3f}")
                    
                    # Условие соседства
                    sin_val = math.sin(math.radians(180 / K_2))
                    neighbor_val = (best_Z2 + 2) / (best_Z1 + best_Z2)
                    
                    with col2:
                        if neighbor_val < sin_val:
                            st.success(f"**Условие соседства:** {neighbor_val:.3f} < {sin_val:.3f} ✅")
                        else:
                            st.error(f"**Условие соседства:** {neighbor_val:.3f} < {sin_val:.3f} ❌")
                    
                    # Условие сборки
                    assembly_check = (best_Z1 + best_Z3) / K_2
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if assembly_check.is_integer():
                            st.success(f"**Условие сборки:** ({best_Z1} + {best_Z3})/{K_2} = {assembly_check} ✅")
                        else:
                            st.error(f"**Условие сборки:** ({best_Z1} + {best_Z3})/{K_2} = {assembly_check} ❌")
                    
                    # Диаграмма
                    with col2:
                        gear_sizes = [best_Z1, best_Z2, best_Z3]
                        st.bar_chart(
                            pd.DataFrame({
                                'Числа зубьев': gear_sizes,
                                'Типы': ['Z1', 'Z2', 'Z3']
                            }).set_index('Типы')
                        )
            else:
                st.error("❌ Подходящие решения не найдены")
                st.info("""
                **Пожалуйста, измените параметры:**
                - Уменьшите значение Z_min
                - Измените значения i_1H или K_2
                - Увеличьте количество итераций
                """)
        
        # Возможность экспорта
        if valid_solutions:
            st.markdown("---")
            st.subheader("📤 Экспорт результатов")
            
            # Подготовка данных для CSV
            export_data = []
            for Z1, Z2, Z3, assembly in valid_solutions:
                export_data.append({
                    "Z1": Z1,
                    "Z2": Z2,
                    "Z3": Z3,
                    "Параметр_сборки": assembly,
                    "i_1H_проверка": round(1 + Z3 / Z1, 3)
                })
            
            export_df = pd.DataFrame(export_data)
            csv = export_df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Скачать результаты в формате CSV",
                data=csv,
                file_name=f"james_gear_i{i_1H}_K{K_2}.csv",
                mime="text/csv"
            )
    
    # Инструкция по использованию
    with st.expander("📖 Инструкция по использованию"):
        st.markdown("""
        ### Расчёт чисел зубьев для механизма Джеймса
        
        **Формулы:**
        - Z2 = (i_1H - 2) / 2 * Z1
        - Z3 = (i_1H - 1) * Z1
        - i_1H = 1 + Z3/Z1
        
        **Обязательные условия:**
        1. **Целочисленность:** Z2 и Z3 должны быть целыми числами
        2. **Условие сборки:** (Z1 + Z3)/K_2 должно быть целым числом
        3. **Условие соседства:** (Z2 + 2)/(Z1 + Z2) < sin(180°/K_2)
        
        **Рекомендуемые параметры:**
        - Z_min: 17-20
        - K_2: 2-4
        - i_1H: 2.0-5.0
        """)
    
    # Футер
    st.markdown("---")
    st.caption("© 2025 Калькулятор Чисел Зубьев Механизма Джеймса | Научная расчётная программа")
    
    # Ссылка на автора
    st.markdown(
        """
        <div style="text-align: center; margin-top: 20px;">
            <p>Разработано с ❤️ для инженерных расчётов</p>
            <p><a href="https://github.com/yagafarov" target="_blank">GitHub автора</a>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()