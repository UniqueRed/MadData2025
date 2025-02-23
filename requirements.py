import json

def create_cs_major_structure():
    major_requirements = {
        "declaration_requirements": {
            "required_courses": ["COMP SCI 300", "MATH 222"],
            "grade_requirement": {
                "course": "COMP SCI 300",
                "min_grade": "BC"
            },
            "gpa_requirement": {
                "courses": ["COMP SCI 300", "MATH 222"],
                "min_gpa": 2.250
            }
        },
        
        "course_sequences": {
            "basic_sequence": [
                {
                    "level": 1,
                    "courses": ["COMP SCI 300"]
                },
                {
                    "level": 2,
                    "courses": [
                        "COMP SCI/MATH 240",
                        "COMP SCI/E C E 252",
                        "COMP SCI/E C E 354",
                        "COMP SCI 400"
                    ]
                }
            ],
            
            "math_requirements": {
                "calculus": {
                    "sequences": [
                        ["MATH 221", "MATH 222"],
                        ["MATH 171", "MATH 217", "MATH 222"]
                    ]
                },
                "linear_algebra": {
                    "one_of": [
                        "MATH 320",
                        "MATH 340",
                        "MATH 341",
                        "MATH 375"
                    ]
                },
                "probability_stats": {
                    "one_of": [
                        "STAT/MATH 309",
                        "STAT 311",
                        "STAT 324",
                        "STAT 333",
                        "STAT 340",
                        "STAT 371",
                        "STAT/MATH 431",
                        "MATH 531"
                    ]
                }
            },
            
            "advanced_requirements": {
                "theory": {
                    "one_of": [
                        "COMP SCI 577",
                        "COMP SCI 520"
                    ]
                },
                "software_hardware": {
                    "required_count": 2,
                    "options": [
                        "COMP SCI 407",
                        "COMP SCI/E C E 506",
                        "COMP SCI 536",
                        "COMP SCI 538",
                        "COMP SCI 537",
                        "COMP SCI 542",
                        "COMP SCI 544",
                        "COMP SCI/E C E 552",
                        "COMP SCI 564",
                        "COMP SCI 640",
                        "COMP SCI 642"
                    ]
                },
                "applications": {
                    "required_count": 1,
                    "options": [
                        "COMP SCI 412",
                        "COMP SCI/I SY E/MATH 425",
                        "COMP SCI/MATH 513",
                        "COMP SCI/MATH 514",
                        "COMP SCI/E C E/I SY E 524",
                        "COMP SCI/I SY E/MATH/STAT 525",
                        "COMP SCI 534",
                        "COMP SCI 540",
                        "COMP SCI 541",
                        "COMP SCI 559",
                        "COMP SCI 565",
                        "COMP SCI 566",
                        "COMP SCI 570",
                        "COMP SCI 571"
                    ]
                }
            }
        },
        
        "course_levels": {
            "introductory": ["COMP SCI 300"],
            "intermediate": [
                "COMP SCI/MATH 240",
                "COMP SCI/E C E 252",
                "COMP SCI/E C E 354",
                "COMP SCI 400"
            ],
            "advanced": {
                "all_courses_numbered": "400-699"
            }
        },
        
        "graduation_requirements": {
            "total_credits": 48,
            "gpa_requirements": {
                "overall_major": 2.000,
                "upper_level": 2.000
            },
            "residence_credits": {
                "comp_sci_credits": 15,
                "upper_level_credits": 15
            }
        }
    }
    
    return major_requirements

# Example usage:
major_data = create_cs_major_structure()

# Save to file
with open('cs_major_requirements.json', 'w') as f:
    json.dump(major_data, f, indent=2)