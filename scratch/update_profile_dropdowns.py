import re
import os

def update_file(filepath):
    print(f"Updating dropdown in: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the profile-dropdown-menu block
    start_tag = '<div id="profile-dropdown-menu"'
    start_idx = content.find(start_tag)
    if start_idx == -1:
        print(f"Could not find profile-dropdown-menu in {filepath}")
        return

    # Find the closing </div> for this profile-dropdown-menu
    # Let's count open/close tags or look for the end block
    # Since we know it ends right before standard script or wrapping divs, we can search for the end pattern
    # In both files, the block ends with '{% endif %}\n                    </div>\n                </div>'
    end_pattern = '{% endif %}\n                    </div>\n                </div>'
    end_idx = content.find(end_pattern, start_idx)
    if end_idx == -1:
        # Check alternative end patterns
        end_pattern = '{% endif %}\n                    </div>\n                </div>'
        # Let's search for a closing tag matching toggleProfileDropdown's parent structure
        # The menu ends right before '</div>\n                </div>' where the user profile button is
        print(f"Searching by closing tags...")
    
    # Let's do a robust search: we know the exact lines in both files!
    # Let's look at the exact block:
    # <div id="profile-dropdown-menu" style="...">
    #     {% if user.is_authenticated %}
    #         ...
    #     {% else %}
    #         ...
    #     {% endif %}
    # </div>
    
    # We want to replace it with a single Logout option:
    new_dropdown = """<div id="profile-dropdown-menu" style="display: none; position: absolute; top: calc(100% + 10px); right: 0; background: white; border-radius: 12px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1); border: 1px solid #f1f5f9; min-width: 160px; z-index: 9999; overflow: hidden; transform-origin: top right; transition: all 0.2s ease;">
                        <a href="{% url 'logout' %}" id="profileLogoutLink" onclick="handleProfileLogout(event)" style="display: flex; align-items: center; gap: 10px; padding: 12px 16px; color: #ef4444; font-size: 0.85rem; font-weight: 700; text-decoration: none; transition: background 0.15s;" onmouseover="this.style.backgroundColor='#fef2f2'" onmouseout="this.style.backgroundColor='transparent'">
                            <i class="fa-solid fa-arrow-right-from-bracket" style="color: #ef4444; font-size: 0.95rem;"></i> Logout
                        </a>
                    </div>"""

    # Let's find the exact text between <div id="profile-dropdown-menu" and the next </div> that matches the end of the menu
    # In index.html:
    # 534:                     <!-- Custom Dropdown Menu -->
    # 535:                     <div id="profile-dropdown-menu" style="display: none; position: absolute; top: calc(100% + 10px); right: 0; background: white; border-radius: 12px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1); border: 1px solid #f1f5f9; min-width: 200px; z-index: 9999; overflow: hidden; transform-origin: top right; transition: all 0.2s ease;">
    # ...
    # 566:                         {% endif %}
    # 567:                     </div>
    
    # We can use regex to find <div id="profile-dropdown-menu".*?{% endif %}\s*</div>
    pattern = r'<div id="profile-dropdown-menu".*?{% endif %}\s*</div>'
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        content = content[:match.start()] + new_dropdown + content[match.end():]
        print("  Replaced dropdown content successfully!")
    else:
        print("  Could not find pattern via regex.")
        return

    # Now let's update the javascript function inside <script> that follows it!
    # In index.html:
    # 570:                 <script>
    # 571:                     function toggleProfileDropdown(e) {
    # ...
    # 595:                 </script>
    
    # We'll replace toggleProfileDropdown & document.click listener, and inject handleProfileLogout and DOMContentLoaded checking!
    new_script = """<script>
                    function toggleProfileDropdown(e) {
                        e.stopPropagation();
                        var menu = document.getElementById("profile-dropdown-menu");
                        if (menu.style.display === "none" || menu.style.display === "") {
                            menu.style.display = "block";
                            menu.style.opacity = "0";
                            menu.style.transform = "scale(0.95)";
                            setTimeout(function() {
                                menu.style.opacity = "1";
                                menu.style.transform = "scale(1)";
                            }, 10);
                        } else {
                            menu.style.display = "none";
                        }
                    }
                    document.addEventListener("click", function(e) {
                        var menu = document.getElementById("profile-dropdown-menu");
                        if (menu && menu.style.display === "block") {
                            var container = document.querySelector(".profile-dropdown-container");
                            if (container && !container.contains(e.target)) {
                                menu.style.display = "none";
                            }
                        }
                    });

                    function handleProfileLogout(e) {
                        e.preventDefault();
                        {% if user.is_authenticated %}
                            localStorage.setItem('showRoleModal', 'true');
                            window.location.href = "{% url 'logout' %}";
                        {% else %}
                            var menu = document.getElementById("profile-dropdown-menu");
                            if (menu) menu.style.display = "none";
                            $('.bd-example-modal-lg').modal('show');
                        {% endif %}
                    }

                    document.addEventListener("DOMContentLoaded", function() {
                        if (localStorage.getItem('showRoleModal') === 'true') {
                            localStorage.removeItem('showRoleModal');
                            $('.bd-example-modal-lg').modal('show');
                        }
                    });
                </script>"""

    # Regex search for <script>.*?toggleProfileDropdown.*?</script>
    script_pattern = r'<script>\s*function toggleProfileDropdown.*?<\/script>'
    script_match = re.search(script_pattern, content, flags=re.DOTALL)
    if script_match:
        content = content[:script_match.start()] + new_script + content[script_match.end():]
        print("  Replaced JavaScript content successfully!")
    else:
        print("  Could not find script block via regex.")
        return

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  Save complete!")

# Run on the current Copy - Copy project
base_path = "c:/Users/SVI/Desktop/Disease Predictor using Machine Learning - Copy - Copy/templates"
update_file(os.path.join(base_path, "homepage/index.html"))
update_file(os.path.join(base_path, "patient/checkdisease/checkdisease.html"))
