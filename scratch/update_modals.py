import re
import os

def update_file(filepath):
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the beautiful new Sign-in modal layout
    new_signin = """<!-- Sign-in Modal -->
<div class="modal fade bd-example-modal-lg" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content" style="border-radius: 24px; border: none; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); overflow: hidden; background: radial-gradient(circle at 5% 5%, #e6fdf5 0%, transparent 35%), radial-gradient(circle at 95% 5%, #f0f9ff 0%, transparent 35%), radial-gradient(circle at 90% 95%, #faf5ff 0%, transparent 30%), #ffffff; position: relative;">
            
            <!-- Background decorative elements -->
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; pointer-events: none; z-index: 0; border-radius: 24px;">
                <!-- Top-left curved vector shapes -->
                <svg style="position: absolute; top: -50px; left: -50px; width: 250px; height: 250px; opacity: 0.45;" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M 0 0 C 120 0, 200 80, 200 200 L 0 200 Z" fill="url(#bgGradGreen)" />
                    <defs>
                        <linearGradient id="bgGradGreen" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#a7f3d0" stop-opacity="0.6"/>
                            <stop offset="100%" stop-color="#34d399" stop-opacity="0.05"/>
                        </linearGradient>
                    </defs>
                </svg>
                <!-- Top-left dots -->
                <svg style="position: absolute; top: 25px; left: 25px; width: 80px; height: 80px; opacity: 0.25;" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <pattern id="dotPattern" x="0" y="0" width="16" height="16" patternUnits="userSpaceOnUse">
                            <circle cx="8" cy="8" r="3" fill="#10b981" />
                        </pattern>
                    </defs>
                    <rect width="100" height="100" fill="url(#dotPattern)" />
                </svg>
                
                <!-- Top-right stethoscope line vector -->
                <svg style="position: absolute; top: 15px; right: 15px; width: 230px; height: 230px; opacity: 0.08;" viewBox="0 0 200 200" fill="none" stroke="#0284c7" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
                    <!-- Elegant stethoscope path -->
                    <path d="M 110 30 C 110 25, 120 15, 135 15 C 150 15, 160 25, 160 40 C 160 60, 140 80, 125 90" />
                    <path d="M 170 35 C 170 25, 160 15, 145 15" />
                    <circle cx="110" cy="30" r="2.5" fill="#0284c7" />
                    <circle cx="170" cy="35" r="2.5" fill="#0284c7" />
                    <path d="M 125 90 C 125 110, 100 130, 85 130 C 70 130, 50 115, 50 95 C 50 75, 70 60, 85 60" />
                    <path d="M 85 130 L 85 150" />
                    <rect x="75" y="150" width="20" height="6" rx="1" fill="#0284c7" stroke="none" />
                    <circle cx="85" cy="168" r="12" stroke-width="2.5" />
                    <circle cx="85" cy="168" r="5" />
                </svg>
            </div>

            <div class="modal-body p-5 text-center" style="position: relative; z-index: 2;">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close" style="position: absolute; top: 25px; right: 30px; border: none; background: none; font-size: 1.8rem; color: #94a3b8; outline: none; cursor: pointer; transition: color 0.15s;" onmouseover="this.style.color='#475569'" onmouseout="this.style.color='#94a3b8'">&times;</button>
                
                <div class="mb-4">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 6px;">
                        <!-- Beautiful custom SVG gradient heart logo matching screenshot exactly -->
                        <svg width="45" height="45" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 4px 6px rgba(16, 185, 129, 0.15));">
                            <defs>
                                <linearGradient id="heartGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" stop-color="#0284c7" />
                                    <stop offset="100%" stop-color="#10b981" />
                                </linearGradient>
                            </defs>
                            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" fill="url(#heartGrad)" />
                            <path d="M6 9h3l1.5-3 1.5 6 1.5-4.5 1.5 1.5h3" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                        <h3 style="font-weight: 800; font-size: 1.8rem; color: #0f172a; margin: 0; font-family: 'Inter', sans-serif;">Disease <span style="color: #10b981;">Predictor</span></h3>
                    </div>
                    <p style="margin: 0; font-size: 0.8rem; letter-spacing: 0.05em; text-transform: uppercase; color: #64748b; font-weight: 700;">AI-Powered Disease Prediction System</p>
                </div>

                <div class="mb-5">
                    <h2 style="font-weight: 800; font-size: 2.2rem; color: #0f172a; margin-bottom: 8px; font-family: 'Inter', sans-serif; letter-spacing: -0.02em;">Welcome to Disease Predictor</h2>
                    <p style="margin: 0; font-size: 0.95rem; color: #64748b; font-weight: 500;">Please choose your role to continue</p>
                    <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin: 16px auto 0 auto; width: 100%; max-width: 250px;">
                        <div style="flex: 1; height: 1px; background: #e2e8f0;"></div>
                        <div style="width: 32px; height: 4px; background: linear-gradient(90deg, #10b981, #3b82f6); border-radius: 2px;"></div>
                        <div style="flex: 1; height: 1px; background: #e2e8f0;"></div>
                    </div>
                </div>

                <div class="row justify-content-center" style="gap: 24px; margin: 0 10px;">
                    <!-- Card 1: Patient -->
                    <div class="col-md-3 p-4" style="border: 1.5px solid #d1fae5; border-radius: 24px; background-color: #ffffff; display: flex; flex-direction: column; align-items: center; transition: all 0.3s ease; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); position: relative; z-index: 5;" onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 12px 24px -10px rgba(16,185,129,0.15)'; this.style.borderColor='#10b981';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px -1px rgba(0,0,0,0.02)'; this.style.borderColor='#d1fae5';">
                        <div style="width: 110px; height: 110px; border-radius: 50%; background-color: #e6fdf5; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto; border: 4px solid #ffffff; box-shadow: 0 4px 12px rgba(16,185,129,0.12); position: relative;">
                            <img src="{% static 'homepage/patient.PNG' %}" alt="Patient" style="width: 80px; height: 80px; object-fit: contain; border-radius: 50%;">
                            <div style="position: absolute; bottom: 0; right: 0; width: 32px; height: 32px; border-radius: 50%; background-color: #10b981; display: flex; align-items: center; justify-content: center; border: 3px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
                                <i class="fa-solid fa-heart-pulse" style="font-size: 0.85rem; color: white;"></i>
                            </div>
                        </div>
                        
                        <h4 style="font-weight: 800; font-size: 1.4rem; color: #16a34a; margin-bottom: 8px;">Patient</h4>
                        <p style="font-size: 0.85rem; color: #64748b; line-height: 1.45; margin-bottom: 24px; min-height: 48px; text-align: center;">Check your symptoms and predict possible diseases.</p>
                        
                        <div class="custom-dropdown" style="position: relative; width: 100%; margin-top: auto;">
                            <div onclick="toggleCardDropdown(this, event)" style="display: flex; justify-content: space-between; align-items: center; padding: 11px 16px; border: 1.5px solid #10b981; border-radius: 12px; background-color: #f0fdf4; color: #15803d; font-weight: 700; font-size: 0.88rem; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.backgroundColor='#e6fdf5'" onmouseout="this.style.backgroundColor='#f0fdf4'">
                                <span>Select an option</span>
                                <i class="fa-solid fa-chevron-down" style="font-size: 0.75rem; color: #15803d;"></i>
                            </div>
                            <div class="card-dropdown-menu" style="display: none; position: absolute; top: calc(100% + 6px); left: 0; right: 0; background: white; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1); z-index: 1000; overflow: hidden;">
                                <a href="{% url 'sign_in_patient' %}" style="display: flex; align-items: center; gap: 10px; padding: 13px 18px; color: #334155; font-size: 0.88rem; font-weight: 600; text-decoration: none; transition: background 0.15s; text-align: left;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='transparent'">
                                    <i class="fa-solid fa-right-to-bracket" style="color: #10b981; font-size: 0.95rem;"></i> Login as Patient
                                </a>
                                <a href="{% url 'signup_patient' %}" style="display: flex; align-items: center; gap: 10px; padding: 13px 18px; color: #334155; font-size: 0.88rem; font-weight: 600; text-decoration: none; border-top: 1px solid #f1f5f9; transition: background 0.15s; text-align: left;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='transparent'">
                                    <i class="fa-solid fa-user-plus" style="color: #10b981; font-size: 0.95rem;"></i> Sign Up as Patient
                                </a>
                            </div>
                        </div>
                    </div>

                    <!-- Card 2: Doctor -->
                    <div class="col-md-3 p-4" style="border: 1.5px solid #e0f2fe; border-radius: 24px; background-color: #ffffff; display: flex; flex-direction: column; align-items: center; transition: all 0.3s ease; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); position: relative; z-index: 5;" onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 12px 24px -10px rgba(59,130,246,0.15)'; this.style.borderColor='#3b82f6';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px -1px rgba(0,0,0,0.02)'; this.style.borderColor='#e0f2fe';">
                        <div style="width: 110px; height: 110px; border-radius: 50%; background-color: #e0f2fe; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto; border: 4px solid #ffffff; box-shadow: 0 4px 12px rgba(59,130,246,0.12); position: relative;">
                            <img src="{% static 'homepage/doctor.PNG' %}" alt="Doctor" style="width: 80px; height: 80px; object-fit: contain; border-radius: 50%;">
                            <div style="position: absolute; bottom: 0; right: 0; width: 32px; height: 32px; border-radius: 50%; background-color: #3b82f6; display: flex; align-items: center; justify-content: center; border: 3px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
                                <i class="fa-solid fa-shield-halved" style="font-size: 0.85rem; color: white;"></i>
                            </div>
                        </div>
                        
                        <h4 style="font-weight: 800; font-size: 1.4rem; color: #2563eb; margin-bottom: 8px;">Doctor</h4>
                        <p style="font-size: 0.85rem; color: #64748b; line-height: 1.45; margin-bottom: 24px; min-height: 48px; text-align: center;">Access patient history and manage consultations.</p>
                        
                        <div class="custom-dropdown" style="position: relative; width: 100%; margin-top: auto;">
                            <div onclick="toggleCardDropdown(this, event)" style="display: flex; justify-content: space-between; align-items: center; padding: 11px 16px; border: 1.5px solid #3b82f6; border-radius: 12px; background-color: #f0f9ff; color: #0369a1; font-weight: 700; font-size: 0.88rem; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.backgroundColor='#e0f2fe'" onmouseout="this.style.backgroundColor='#f0f9ff'">
                                <span>Select an option</span>
                                <i class="fa-solid fa-chevron-down" style="font-size: 0.75rem; color: #0369a1;"></i>
                            </div>
                            <div class="card-dropdown-menu" style="display: none; position: absolute; top: calc(100% + 6px); left: 0; right: 0; background: white; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1); z-index: 1000; overflow: hidden;">
                                <a href="{% url 'sign_in_doctor' %}" style="display: flex; align-items: center; gap: 10px; padding: 13px 18px; color: #334155; font-size: 0.88rem; font-weight: 600; text-decoration: none; transition: background 0.15s; text-align: left;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='transparent'">
                                    <i class="fa-solid fa-right-to-bracket" style="color: #3b82f6; font-size: 0.95rem;"></i> Login as Doctor
                                </a>
                                <a href="{% url 'signup_doctor' %}" style="display: flex; align-items: center; gap: 10px; padding: 13px 18px; color: #334155; font-size: 0.88rem; font-weight: 600; text-decoration: none; border-top: 1px solid #f1f5f9; transition: background 0.15s; text-align: left;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='transparent'">
                                    <i class="fa-solid fa-user-plus" style="color: #3b82f6; font-size: 0.95rem;"></i> Sign Up as Doctor
                                </a>
                            </div>
                        </div>
                    </div>

                    <!-- Card 3: Admin -->
                    <div class="col-md-3 p-4" style="border: 1.5px solid #f3e8ff; border-radius: 24px; background-color: #ffffff; display: flex; flex-direction: column; align-items: center; transition: all 0.3s ease; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); position: relative; z-index: 5;" onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 12px 24px -10px rgba(139,92,246,0.15)'; this.style.borderColor='#a855f7';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px -1px rgba(0,0,0,0.02)'; this.style.borderColor='#f3e8ff';">
                        <div style="width: 110px; height: 110px; border-radius: 50%; background-color: #f3e8ff; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto; border: 4px solid #ffffff; box-shadow: 0 4px 12px rgba(139,92,246,0.12); position: relative;">
                            <img src="{% static 'homepage/admin.PNG' %}" alt="Admin" style="width: 80px; height: 80px; object-fit: contain; border-radius: 50%;">
                            <div style="position: absolute; bottom: 0; right: 0; width: 32px; height: 32px; border-radius: 50%; background-color: #a855f7; display: flex; align-items: center; justify-content: center; border: 3px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
                                <i class="fa-solid fa-gear" style="font-size: 0.85rem; color: white;"></i>
                            </div>
                        </div>
                        
                        <h4 style="font-weight: 800; font-size: 1.4rem; color: #7c3aed; margin-bottom: 8px;">Admin</h4>
                        <p style="font-size: 0.85rem; color: #64748b; line-height: 1.45; margin-bottom: 24px; min-height: 48px; text-align: center;">Manage users, doctors and system activities.</p>
                        
                        <div class="custom-dropdown" style="position: relative; width: 100%; margin-top: auto;">
                            <div onclick="toggleCardDropdown(this, event)" style="display: flex; justify-content: space-between; align-items: center; padding: 11px 16px; border: 1.5px solid #a855f7; border-radius: 12px; background-color: #faf5ff; color: #6d28d9; font-weight: 700; font-size: 0.88rem; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.backgroundColor='#f3e8ff'" onmouseout="this.style.backgroundColor='#faf5ff'">
                                <span>Select an option</span>
                                <i class="fa-solid fa-chevron-down" style="font-size: 0.75rem; color: #6d28d9;"></i>
                            </div>
                            <div class="card-dropdown-menu" style="display: none; position: absolute; top: calc(100% + 6px); left: 0; right: 0; background: white; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1); z-index: 1000; overflow: hidden;">
                                <a href="{% url 'sign_in_admin' %}" style="display: flex; align-items: center; gap: 10px; padding: 13px 18px; color: #334155; font-size: 0.88rem; font-weight: 600; text-decoration: none; transition: background 0.15s; text-align: left;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='transparent'">
                                    <i class="fa-solid fa-right-to-bracket" style="color: #a855f7; font-size: 0.95rem;"></i> Login as Admin
                                </a>
                                <a href="{% url 'sign_in_admin' %}" style="display: flex; align-items: center; gap: 10px; padding: 13px 18px; color: #334155; font-size: 0.88rem; font-weight: 600; text-decoration: none; border-top: 1px solid #f1f5f9; transition: background 0.15s; text-align: left;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='transparent'">
                                    <i class="fa-solid fa-user-plus" style="color: #a855f7; font-size: 0.95rem;"></i> Sign Up as Admin
                                </a>
                            </div>
                        </div>
                    </div>
                </div>

                <div style="display: inline-flex; align-items: center; gap: 8px; background-color: #ecfdf5; border: 1px solid #a7f3d0; padding: 11px 28px; border-radius: 30px; margin: 36px auto 0 auto; font-size: 0.85rem; color: #065f46; font-weight: 600; box-shadow: 0 2px 4px rgba(16, 185, 129, 0.05);">
                    <i class="fa-solid fa-shield-halved" style="color: #10b981; font-size: 1.05rem;"></i>
                    <span>Your data is safe and secure with us.</span>
                </div>
            </div>
        </div>
    </div>
</div>"""

    # Define the beautiful new Sign-up modal layout
    new_signup = """<!-- Sign-up Modal (Uses Same Unified Selector Screen) -->
<div class="modal fade bd-example-modal-lg2" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content" style="border-radius: 24px; border: none; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); overflow: hidden; background: radial-gradient(circle at 5% 5%, #e6fdf5 0%, transparent 35%), radial-gradient(circle at 95% 5%, #f0f9ff 0%, transparent 35%), radial-gradient(circle at 90% 95%, #faf5ff 0%, transparent 30%), #ffffff; position: relative;">
            
            <!-- Background decorative elements -->
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; pointer-events: none; z-index: 0; border-radius: 24px;">
                <!-- Top-left curved vector shapes -->
                <svg style="position: absolute; top: -50px; left: -50px; width: 250px; height: 250px; opacity: 0.45;" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M 0 0 C 120 0, 200 80, 200 200 L 0 200 Z" fill="url(#bgGradGreen2)" />
                    <defs>
                        <linearGradient id="bgGradGreen2" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#a7f3d0" stop-opacity="0.6"/>
                            <stop offset="100%" stop-color="#34d399" stop-opacity="0.05"/>
                        </linearGradient>
                    </defs>
                </svg>
                <!-- Top-left dots -->
                <svg style="position: absolute; top: 25px; left: 25px; width: 80px; height: 80px; opacity: 0.25;" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <pattern id="dotPattern2" x="0" y="0" width="16" height="16" patternUnits="userSpaceOnUse">
                            <circle cx="8" cy="8" r="3" fill="#10b981" />
                        </pattern>
                    </defs>
                    <rect width="100" height="100" fill="url(#dotPattern2)" />
                </svg>
                
                <!-- Top-right stethoscope line vector -->
                <svg style="position: absolute; top: 15px; right: 15px; width: 230px; height: 230px; opacity: 0.08;" viewBox="0 0 200 200" fill="none" stroke="#0284c7" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
                    <!-- Elegant stethoscope path -->
                    <path d="M 110 30 C 110 25, 120 15, 135 15 C 150 15, 160 25, 160 40 C 160 60, 140 80, 125 90" />
                    <path d="M 170 35 C 170 25, 160 15, 145 15" />
                    <circle cx="110" cy="30" r="2.5" fill="#0284c7" />
                    <circle cx="170" cy="35" r="2.5" fill="#0284c7" />
                    <path d="M 125 90 C 125 110, 100 130, 85 130 C 70 130, 50 115, 50 95 C 50 75, 70 60, 85 60" />
                    <path d="M 85 130 L 85 150" />
                    <rect x="75" y="150" width="20" height="6" rx="1" fill="#0284c7" stroke="none" />
                    <circle cx="85" cy="168" r="12" stroke-width="2.5" />
                    <circle cx="85" cy="168" r="5" />
                </svg>
            </div>

            <div class="modal-body p-5 text-center" style="position: relative; z-index: 2;">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close" style="position: absolute; top: 25px; right: 30px; border: none; background: none; font-size: 1.8rem; color: #94a3b8; outline: none; cursor: pointer; transition: color 0.15s;" onmouseover="this.style.color='#475569'" onmouseout="this.style.color='#94a3b8'">&times;</button>
                
                <div class="mb-4">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 6px;">
                        <!-- Beautiful custom SVG gradient heart logo matching screenshot exactly -->
                        <svg width="45" height="45" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 4px 6px rgba(16, 185, 129, 0.15));">
                            <defs>
                                <linearGradient id="heartGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" stop-color="#0284c7" />
                                    <stop offset="100%" stop-color="#10b981" />
                                </linearGradient>
                            </defs>
                            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" fill="url(#heartGrad2)" />
                            <path d="M6 9h3l1.5-3 1.5 6 1.5-4.5 1.5 1.5h3" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                        <h3 style="font-weight: 800; font-size: 1.8rem; color: #0f172a; margin: 0; font-family: 'Inter', sans-serif;">Disease <span style="color: #10b981;">Predictor</span></h3>
                    </div>
                    <p style="margin: 0; font-size: 0.8rem; letter-spacing: 0.05em; text-transform: uppercase; color: #64748b; font-weight: 700;">AI-Powered Disease Prediction System</p>
                </div>

                <div class="mb-5">
                    <h2 style="font-weight: 800; font-size: 2.2rem; color: #0f172a; margin-bottom: 8px; font-family: 'Inter', sans-serif; letter-spacing: -0.02em;">Welcome to Disease Predictor</h2>
                    <p style="margin: 0; font-size: 0.95rem; color: #64748b; font-weight: 500;">Please choose your role to continue</p>
                    <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin: 16px auto 0 auto; width: 100%; max-width: 250px;">
                        <div style="flex: 1; height: 1px; background: #e2e8f0;"></div>
                        <div style="width: 32px; height: 4px; background: linear-gradient(90deg, #10b981, #3b82f6); border-radius: 2px;"></div>
                        <div style="flex: 1; height: 1px; background: #e2e8f0;"></div>
                    </div>
                </div>

                <div class="row justify-content-center" style="gap: 24px; margin: 0 10px;">
                    <!-- Card 1: Patient -->
                    <div class="col-md-3 p-4" style="border: 1.5px solid #d1fae5; border-radius: 24px; background-color: #ffffff; display: flex; flex-direction: column; align-items: center; transition: all 0.3s ease; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); position: relative; z-index: 5;" onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 12px 24px -10px rgba(16,185,129,0.15)'; this.style.borderColor='#10b981';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px -1px rgba(0,0,0,0.02)'; this.style.borderColor='#d1fae5';">
                        <div style="width: 110px; height: 110px; border-radius: 50%; background-color: #e6fdf5; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto; border: 4px solid #ffffff; box-shadow: 0 4px 12px rgba(16,185,129,0.12); position: relative;">
                            <img src="{% static 'homepage/patient.PNG' %}" alt="Patient" style="width: 80px; height: 80px; object-fit: contain; border-radius: 50%;">
                            <div style="position: absolute; bottom: 0; right: 0; width: 32px; height: 32px; border-radius: 50%; background-color: #10b981; display: flex; align-items: center; justify-content: center; border: 3px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
                                <i class="fa-solid fa-heart-pulse" style="font-size: 0.85rem; color: white;"></i>
                            </div>
                        </div>
                        
                        <h4 style="font-weight: 800; font-size: 1.4rem; color: #16a34a; margin-bottom: 8px;">Patient</h4>
                        <p style="font-size: 0.85rem; color: #64748b; line-height: 1.45; margin-bottom: 24px; min-height: 48px; text-align: center;">Check your symptoms and predict possible diseases.</p>
                        
                        <div class="custom-dropdown" style="position: relative; width: 100%; margin-top: auto;">
                            <div onclick="toggleCardDropdown(this, event)" style="display: flex; justify-content: space-between; align-items: center; padding: 11px 16px; border: 1.5px solid #10b981; border-radius: 12px; background-color: #f0fdf4; color: #15803d; font-weight: 700; font-size: 0.88rem; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.backgroundColor='#e6fdf5'" onmouseout="this.style.backgroundColor='#f0fdf4'">
                                <span>Select an option</span>
                                <i class="fa-solid fa-chevron-down" style="font-size: 0.75rem; color: #15803d;"></i>
                            </div>
                            <div class="card-dropdown-menu" style="display: none; position: absolute; top: calc(100% + 6px); left: 0; right: 0; background: white; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1); z-index: 1000; overflow: hidden;">
                                <a href="{% url 'sign_in_patient' %}" style="display: flex; align-items: center; gap: 10px; padding: 13px 18px; color: #334155; font-size: 0.88rem; font-weight: 600; text-decoration: none; transition: background 0.15s; text-align: left;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='transparent'">
                                    <i class="fa-solid fa-right-to-bracket" style="color: #10b981; font-size: 0.95rem;"></i> Login as Patient
                                </a>
                                <a href="{% url 'signup_patient' %}" style="display: flex; align-items: center; gap: 10px; padding: 13px 18px; color: #334155; font-size: 0.88rem; font-weight: 600; text-decoration: none; border-top: 1px solid #f1f5f9; transition: background 0.15s; text-align: left;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='transparent'">
                                    <i class="fa-solid fa-user-plus" style="color: #10b981; font-size: 0.95rem;"></i> Sign Up as Patient
                                </a>
                            </div>
                        </div>
                    </div>

                    <!-- Card 2: Doctor -->
                    <div class="col-md-3 p-4" style="border: 1.5px solid #e0f2fe; border-radius: 24px; background-color: #ffffff; display: flex; flex-direction: column; align-items: center; transition: all 0.3s ease; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); position: relative; z-index: 5;" onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 12px 24px -10px rgba(59,130,246,0.15)'; this.style.borderColor='#3b82f6';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px -1px rgba(0,0,0,0.02)'; this.style.borderColor='#e0f2fe';">
                        <div style="width: 110px; height: 110px; border-radius: 50%; background-color: #e0f2fe; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto; border: 4px solid #ffffff; box-shadow: 0 4px 12px rgba(59,130,246,0.12); position: relative;">
                            <img src="{% static 'homepage/doctor.PNG' %}" alt="Doctor" style="width: 80px; height: 80px; object-fit: contain; border-radius: 50%;">
                            <div style="position: absolute; bottom: 0; right: 0; width: 32px; height: 32px; border-radius: 50%; background-color: #3b82f6; display: flex; align-items: center; justify-content: center; border: 3px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
                                <i class="fa-solid fa-shield-halved" style="font-size: 0.85rem; color: white;"></i>
                            </div>
                        </div>
                        
                        <h4 style="font-weight: 800; font-size: 1.4rem; color: #2563eb; margin-bottom: 8px;">Doctor</h4>
                        <p style="font-size: 0.85rem; color: #64748b; line-height: 1.45; margin-bottom: 24px; min-height: 48px; text-align: center;">Access patient history and manage consultations.</p>
                        
                        <div class="custom-dropdown" style="position: relative; width: 100%; margin-top: auto;">
                            <div onclick="toggleCardDropdown(this, event)" style="display: flex; justify-content: space-between; align-items: center; padding: 11px 16px; border: 1.5px solid #3b82f6; border-radius: 12px; background-color: #f0f9ff; color: #0369a1; font-weight: 700; font-size: 0.88rem; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.backgroundColor='#e0f2fe'" onmouseout="this.style.backgroundColor='#f0f9ff'">
                                <span>Select an option</span>
                                <i class="fa-solid fa-chevron-down" style="font-size: 0.75rem; color: #0369a1;"></i>
                            </div>
                            <div class="card-dropdown-menu" style="display: none; position: absolute; top: calc(100% + 6px); left: 0; right: 0; background: white; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1); z-index: 1000; overflow: hidden;">
                                <a href="{% url 'sign_in_doctor' %}" style="display: flex; align-items: center; gap: 10px; padding: 13px 18px; color: #334155; font-size: 0.88rem; font-weight: 600; text-decoration: none; transition: background 0.15s; text-align: left;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='transparent'">
                                    <i class="fa-solid fa-right-to-bracket" style="color: #3b82f6; font-size: 0.95rem;"></i> Login as Doctor
                                </a>
                                <a href="{% url 'signup_doctor' %}" style="display: flex; align-items: center; gap: 10px; padding: 13px 18px; color: #334155; font-size: 0.88rem; font-weight: 600; text-decoration: none; border-top: 1px solid #f1f5f9; transition: background 0.15s; text-align: left;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='transparent'">
                                    <i class="fa-solid fa-user-plus" style="color: #3b82f6; font-size: 0.95rem;"></i> Sign Up as Doctor
                                </a>
                            </div>
                        </div>
                    </div>

                    <!-- Card 3: Admin -->
                    <div class="col-md-3 p-4" style="border: 1.5px solid #f3e8ff; border-radius: 24px; background-color: #ffffff; display: flex; flex-direction: column; align-items: center; transition: all 0.3s ease; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); position: relative; z-index: 5;" onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 12px 24px -10px rgba(139,92,246,0.15)'; this.style.borderColor='#a855f7';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px -1px rgba(0,0,0,0.02)'; this.style.borderColor='#f3e8ff';">
                        <div style="width: 110px; height: 110px; border-radius: 50%; background-color: #f3e8ff; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto; border: 4px solid #ffffff; box-shadow: 0 4px 12px rgba(139,92,246,0.12); position: relative;">
                            <img src="{% static 'homepage/admin.PNG' %}" alt="Admin" style="width: 80px; height: 80px; object-fit: contain; border-radius: 50%;">
                            <div style="position: absolute; bottom: 0; right: 0; width: 32px; height: 32px; border-radius: 50%; background-color: #a855f7; display: flex; align-items: center; justify-content: center; border: 3px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
                                <i class="fa-solid fa-gear" style="font-size: 0.85rem; color: white;"></i>
                            </div>
                        </div>
                        
                        <h4 style="font-weight: 800; font-size: 1.4rem; color: #7c3aed; margin-bottom: 8px;">Admin</h4>
                        <p style="font-size: 0.85rem; color: #64748b; line-height: 1.45; margin-bottom: 24px; min-height: 48px; text-align: center;">Manage users, doctors and system activities.</p>
                        
                        <div class="custom-dropdown" style="position: relative; width: 100%; margin-top: auto;">
                            <div onclick="toggleCardDropdown(this, event)" style="display: flex; justify-content: space-between; align-items: center; padding: 11px 16px; border: 1.5px solid #a855f7; border-radius: 12px; background-color: #faf5ff; color: #6d28d9; font-weight: 700; font-size: 0.88rem; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.backgroundColor='#f3e8ff'" onmouseout="this.style.backgroundColor='#faf5ff'">
                                <span>Select an option</span>
                                <i class="fa-solid fa-chevron-down" style="font-size: 0.75rem; color: #6d28d9;"></i>
                            </div>
                            <div class="card-dropdown-menu" style="display: none; position: absolute; top: calc(100% + 6px); left: 0; right: 0; background: white; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1); z-index: 1000; overflow: hidden;">
                                <a href="{% url 'sign_in_admin' %}" style="display: flex; align-items: center; gap: 10px; padding: 13px 18px; color: #334155; font-size: 0.88rem; font-weight: 600; text-decoration: none; transition: background 0.15s; text-align: left;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='transparent'">
                                    <i class="fa-solid fa-right-to-bracket" style="color: #a855f7; font-size: 0.95rem;"></i> Login as Admin
                                </a>
                                <a href="{% url 'sign_in_admin' %}" style="display: flex; align-items: center; gap: 10px; padding: 13px 18px; color: #334155; font-size: 0.88rem; font-weight: 600; text-decoration: none; border-top: 1px solid #f1f5f9; transition: background 0.15s; text-align: left;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='transparent'">
                                    <i class="fa-solid fa-user-plus" style="color: #a855f7; font-size: 0.95rem;"></i> Sign Up as Admin
                                </a>
                            </div>
                        </div>
                    </div>
                </div>

                <div style="display: inline-flex; align-items: center; gap: 8px; background-color: #ecfdf5; border: 1px solid #a7f3d0; padding: 11px 28px; border-radius: 30px; margin: 36px auto 0 auto; font-size: 0.85rem; color: #065f46; font-weight: 600; box-shadow: 0 2px 4px rgba(16, 185, 129, 0.05);">
                    <i class="fa-solid fa-shield-halved" style="color: #10b981; font-size: 1.05rem;"></i>
                    <span>Your data is safe and secure with us.</span>
                </div>
            </div>
        </div>
    </div>
</div>"""

    # For index.html, replace the second modal using regex/string find
    if "index.html" in filepath:
        # Find index of second modal and replace it
        start_idx = content.find('<!-- Sign-up Modal (Uses Same Unified Selector Screen) -->')
        if start_idx != -1:
            end_idx = content.find('<script>', start_idx)
            # Find the closing </div> of the modal right before <script>
            end_div_idx = content.rfind('</div>', start_idx, end_idx)
            # Find the very last </div> of that modal
            # To be safe, we can just replace from start_idx up to the start of the <script> block (excluding script)
            # Let's see: the last line before <script> was indeed </div>
            target_block = content[start_idx:end_idx].strip()
            print("Found old Sign-up Modal in index.html, replacing...")
            content = content[:start_idx] + new_signup + "\n\n" + content[end_idx:]
        else:
            print("Could not find Sign-up Modal in index.html by comment. Trying regex...")
            # Fallback if comment is missing
            pattern = r'<div class="modal fade bd-example-modal-lg2".*?</div>\s*(?=<script>)'
            content = re.sub(pattern, new_signup, content, flags=re.DOTALL)

    # For basic.html, replace both modals
    elif "basic.html" in filepath:
        # Sign-in modal
        start_idx = content.find('<!-- Sign-in Modal -->')
        if start_idx != -1:
            end_idx = content.find('<!-- Sign-up Modal -->')
            if end_idx != -1:
                print("Replacing Sign-in Modal in basic.html...")
                content = content[:start_idx] + new_signin + "\n\n  " + content[end_idx:]
        
        # Sign-up modal
        start_idx = content.find('<!-- Sign-up Modal -->')
        if start_idx == -1:
            # Maybe it is comment '<!-- Sign-up Modal (Uses Same Unified Selector Screen) -->'
            start_idx = content.find('<!-- Sign-up Modal (Uses Same Unified Selector Screen) -->')
            if start_idx == -1:
                start_idx = content.find('bd-example-modal-lg2')
                # backtrack to comment
                if start_idx != -1:
                    start_idx = content.rfind('<!--', 0, start_idx)

        if start_idx != -1:
            end_idx = content.find('<script>', start_idx)
            if end_idx != -1:
                print("Replacing Sign-up Modal in basic.html...")
                content = content[:start_idx] + new_signup + "\n\n  " + content[end_idx:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Success!")

# Run on the current Copy - Copy project
base_path = "c:/Users/SVI/Desktop/Disease Predictor using Machine Learning - Copy - Copy/templates"
update_file(os.path.join(base_path, "homepage/index.html"))
update_file(os.path.join(base_path, "basic.html"))
