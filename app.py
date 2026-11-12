# --- TAB 3: CFA & Validity ---
with tab_cfa:
    if st.session_state['phase2_data'] is not None and selected_items:
        n_cases_cfa = len(st.session_state['phase2_data'])
        if n_cases_cfa < 50:
            st.error(lang['sample_warning'])
        else:
            efa_out = st.session_state.get('efa_output')
            default_cfa_factors = int(efa_out['factor_count']) if efa_out else 2
            cfa_factors = st.number_input("CFA Factors", min_value=1, value=default_cfa_factors, key="cfa_factors")
            
            labels = [f"Factor_{i+1}" for i in range(cfa_factors)]
            options = ["غير مدرج (Not included)"] + labels
            
            st.markdown("#### توزيع الفقرات على العوامل")
            
            # 1. جلب التوزيعات من EFA
            efa_assignments = st.session_state.get('item_assignments') or {}
            
            if efa_assignments:
                st.info(lang['auto_assign_msg'])
                
                # 2. التحديث الإجباري لحالة Streamlit لكل قائمة منسدلة
                # نتحقق إذا كانت القيمة لم تُعين بعد في session_state الحالية
                for item in selected_items:
                    widget_key = f"cfa_select_{item}"
                    if widget_key not in st.session_state:
                        # نجلب القيمة المقترحة من EFA، ونتأكد أنها ضمن الخيارات المتاحة
                        proposed_val = efa_assignments.get(item, "غير مدرج (Not included)")
                        if proposed_val not in options:
                            proposed_val = "غير مدرج (Not included)"
                        # نحقن القيمة مباشرة في session_state
                        st.session_state[widget_key] = proposed_val
            
            assign = {}
            cols = st.columns(2)
            
            # 3. رسم القوائم المنسدلة
            for i, item in enumerate(selected_items):
                widget_key = f"cfa_select_{item}"
                
                # الآن نترك Streamlit يعتمد كليًا على الـ key لقراءة القيمة
                assign[item] = cols[i%2].selectbox(
                    label=str(item), 
                    options=options, 
                    key=widget_key
                )
            
            if st.button(lang['run_cfa']):
                f_assign = {f: [i for i, a in assign.items() if a == f] for f in labels}
                f_assign = {k: v for k, v in f_assign.items() if len(v) > 0}
                
                if not f_assign or any(len(v) < 2 for v in f_assign.values()):
                    st.error("⚠️ فشل بناء النموذج: أحد العوامل يحتوي على أقل من فقرتين. تأكد من تحديد فقرتين على الأقل لكل عامل لتجنب أخطاء البناء.")
                else:
                    try:
                        spec = build_cfa_specification(f_assign)
                        cfa_out = cfa_result(st.session_state['phase2_data'], spec)
                        st.session_state['cfa_output'] = cfa_out
                        st.success("CFA Completed Successfully!")
                        
                        st.markdown("#### مؤشرات جودة المطابقة (Fit Indices)")
                        fit_vals = cfa_out["fit"]
                        f_cols = st.columns(4)
                        f_cols[0].metric("CFI", f"{fit_vals['CFI']:.3f}")
                        f_cols[1].metric("TLI", f"{fit_vals['TLI']:.3f}")
                        f_cols[2].metric("RMSEA", f"{fit_vals['RMSEA']:.3f}")
                        f_cols[3].metric("χ² (df)", f"{fit_vals['chi2']:.2f} ({fit_vals['DoF']:.0f})")
                        
                        st.markdown("#### تقديرات معلمات النموذج (Parameter Estimates)")
                        params_df = cfa_out["params"]
                        display_params = params_df[(params_df['op'] == '~') & (params_df['rval'].isin(labels))].copy()
                        display_params = display_params.rename(columns={'rval': 'Factor', 'lval_orig': 'Item'})
                        cols_to_show = ['Factor', 'Item', 'Estimate', 'Est. Std', 'Std. Err', 'z-value', 'p-value']
                        cols_to_show = [c for c in cols_to_show if c in display_params.columns]
                        
                        numeric_cols = ['Estimate', 'Est. Std', 'Std. Err', 'z-value', 'p-value']
                        for col in numeric_cols:
                            if col in display_params.columns:
                                display_params[col] = pd.to_numeric(display_params[col], errors='coerce')

                        st.dataframe(display_params[cols_to_show].style.format({
                            "Estimate": "{:.3f}", 
                            "Est. Std": "{:.3f}", 
                            "Std. Err": "{:.3f}", 
                            "z-value": "{:.3f}", 
                            "p-value": "{:.4f}"
                        }, na_rep="—"), use_container_width=True)

                        # --- Automated Diagnostic System (نظام التشخيص الآلي - JARS/APA 7) ---
                        st.markdown("---")
                        st.markdown("### 🛠️ نظام التوجيه والتشخيص الآلي (JARS / APA 7)")
                        
                        cr_ave_data = cfa_out.get('cr_ave', {})
                        factors_list = list(f_assign.keys())
                        
                        st.markdown("#### 1. الصدق التقاربي والثبات (Convergent Validity & Reliability)")
                        
                        if cr_ave_data:
                            val_data = []
                            issues_found = [] 
                            
                            for factor, metrics in cr_ave_data.items():
                                alpha, omega = calc_alpha_omega(st.session_state['phase2_data'], f_assign[factor])
                                cr_val = metrics['CR']
                                ave_val = metrics['AVE']
                                
                                val_data.append({
                                    "العامل (Factor)": factor,
                                    "ألفا كرونباخ (α)": alpha,
                                    "أوميغا (ω)": omega,
                                    "الثبات المركب (CR)": cr_val,
                                    "التباين المستخرج (AVE)": ave_val
                                })
                                
                                if ave_val < 0.50:
                                    issues_found.append(f"العامل **{factor}**: قيمة AVE ({ave_val:.3f}) أقل من 0.50.")
                                if cr_val < 0.70:
                                    issues_found.append(f"العامل **{factor}**: قيمة CR ({cr_val:.3f}) أقل من 0.70.")
                            
                            val_df = pd.DataFrame(val_data).set_index("العامل (Factor)")
                            st.dataframe(val_df.style.format("{:.3f}"), use_container_width=True)
                            
                            if issues_found:
                                st.error("❌ **تحذير معايير JARS:** لم يتحقق الصدق التقاربي أو الثبات في بعض العوامل.")
                                for issue in issues_found:
                                    st.warning(f"⚠️ {issue}")
                                st.info("💡 **الحل المقترح:** اصعد للأعلى وقم بتغيير حالة الفقرات ذات التشبع الضعيف (أقل من 0.50) في هذا العامل إلى 'غير مدرج' ثم أعد التحليل.")
                            else:
                                st.success("✅ **ممتاز:** جميع قيم الصدق التقاربي (AVE > 0.50) والثبات المركب (CR > 0.70) مطابقة للمعايير.")

                        st.markdown("#### 2. الصدق التمييزي (Discriminant Validity - Fornell-Larcker)")
                        
                        disc_df = pd.DataFrame(index=factors_list, columns=factors_list, dtype=float)
                        
                        for f in factors_list:
                            if f in cr_ave_data:
                                disc_df.loc[f, f] = np.sqrt(cr_ave_data[f]['AVE'])
                                
                        corrs = params_df[(params_df['op'] == '~~') & (params_df['lval'].isin(factors_list)) & (params_df['rval'].isin(factors_list)) & (params_df['lval'] != params_df['rval'])]
                        for _, row in corrs.iterrows():
                            f1, f2 = row['lval'], row['rval']
                            val = float(row['Est. Std'])
                            disc_df.loc[f1, f2] = val
                            disc_df.loc[f2, f1] = val
                                
                        def highlight_diag(df):
                            attr = 'background-color: #d1fae5; font-weight: bold; color: #065f46;'
                            return pd.DataFrame(np.where(np.eye(df.shape[0], dtype=bool), attr, ''), index=df.index, columns=df.columns)
                            
                        st.dataframe(disc_df.style.apply(highlight_diag, axis=None).format("{:.3f}", na_rep="—"), use_container_width=True)
                        
                        disc_issues = []
                        for i, f1 in enumerate(factors_list):
                            for j, f2 in enumerate(factors_list):
                                if i != j and pd.notna(disc_df.loc[f1, f2]) and pd.notna(disc_df.loc[f1, f1]):
                                    if abs(disc_df.loc[f1, f2]) > disc_df.loc[f1, f1]:
                                        disc_issues.append(f"الارتباط بين ({f1}) و ({f2}) = {abs(disc_df.loc[f1, f2]):.3f} وهو أعلى من الجذر التربيعي لـ AVE للعامل ({f1}) = {disc_df.loc[f1, f1]:.3f}")
                        
                        if disc_issues:
                            st.error("❌ **تحذير معايير JARS:** لم يتحقق الصدق التمييزي (معيار Fornell-Larcker).")
                            for d_issue in disc_issues:
                                st.warning(f"⚠️ التداخل العالي: {d_issue}")
                            st.info("💡 **الحل المقترح:** هناك تداخل كبير بين هذه العوامل (Cross-loadings). راجع الفقرات المشتركة أو المتقاربة في المعنى بين هذه العوامل وقم بحذف الأضعف منها، أو فكر في دمج العاملين إذا كان التداخل نظرياً منطقياً.")
                        else:
                            st.success("✅ **ممتاز:** الصدق التمييزي متحقق بنجاح. قيم الجذر التربيعي لـ AVE (في القطر الأخضر) أعلى من جميع الارتباطات الأخرى.")

                        st.markdown("#### المخطط الهيكلي (Structural Diagram)")
                        dot_code = "digraph CFA {\nrankdir=LR;\nnode [shape=box, style=filled, fillcolor=white];\n"
                        for factor, items in f_assign.items():
                            dot_code += f'"{factor}" [shape=ellipse, style=filled, fillcolor="#bae6fd"];\n'
                            for item in items:
                                dot_code += f'"{factor}" -> "{item}";\n'
                        dot_code += "}"
                        st.graphviz_chart(dot_code)

                    except Exception as e:
                        st.error(f"⚠️ فشل التحليل التوكيدي: يرجى التأكد من أن البيانات مناسبة لبناء النموذج. (تفاصيل الخطأ: {str(e)})")
