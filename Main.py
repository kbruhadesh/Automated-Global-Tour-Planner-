import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import numpy as np
from tkcalendar import DateEntry
from typing import List, Dict, Tuple, Set
import json

with open('data.json', 'r') as file:
    country_data = json.load(file)

class CountryData:
    def __init__(self, country_data: Dict):
        self.countries_data = country_data
        self.all_interests = sorted(list(set(
            interest for country in self.countries_data.values() 
            for interest in country['interests']
        )))

class TourOptimizer:
    def __init__(self, country_data: CountryData):
        self.country_data = country_data

    def calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        return np.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

    def solve_tsp(self, selected_countries: List[str], home_country: str) -> List[str]:
        if not selected_countries:
            return []
        
        if home_country in selected_countries:
            selected_countries.remove(home_country)
        
        route = [home_country]
        unvisited = set(selected_countries)
        current = home_country

        while unvisited:
            next_country = min(
                unvisited,
                key=lambda x: self.calculate_distance(
                    self.country_data.countries_data[current]["coordinates"],
                    self.country_data.countries_data[x]["coordinates"]
                )
            )
            route.append(next_country)
            unvisited.remove(next_country)
            current = next_country

        route.append(home_country)
        return route

    def calculate_country_interest_score(self, country: str, selected_interests: Set[str]) -> int:
        country_interests = set(self.country_data.countries_data[country]["interests"])
        return len(country_interests.intersection(selected_interests))

    def distribute_days(self, total_days: int, route: List[str], 
                       selected_interests: Set[str]) -> Dict[str, int]:
        days_per_country = {}
        countries = route[1:-1]  

        interest_scores = {
            country: self.calculate_country_interest_score(country, selected_interests)
            for country in countries
        }
        
        total_score = sum(interest_scores.values())
        if total_score == 0:
            base_days = total_days // len(countries)
            days_per_country = {country: base_days for country in countries}
        else:
            remaining_days = total_days
            min_days = 2
            
            for country in countries:
                days_per_country[country] = min_days
                remaining_days -= min_days
            
            for country in countries:
                if total_score > 0:
                    additional_days = int((remaining_days * interest_scores[country]) / total_score)
                    days_per_country[country] += additional_days
                    remaining_days -= additional_days
            
            sorted_countries = sorted(
                countries,
                key=lambda x: (interest_scores[x], -days_per_country[x]),
                reverse=True
            )
            
            for country in sorted_countries:
                if remaining_days > 0:
                    days_per_country[country] += 1
                    remaining_days -= 1
                else:
                    break
                    
        return days_per_country

class TourPlannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("✈️ Global Tour Planner")
        self.country_data = CountryData(country_data)
        self.optimizer = TourOptimizer(self.country_data)
        
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('Subheader.TLabel', font=('Helvetica', 11))
        style.configure('Custom.TButton', font=('Helvetica', 10))
        
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        self.input_frame = ttk.LabelFrame(main_frame, padding="15", text="Travel Parameters")
        self.input_frame.grid(row=0, column=0, sticky="nsew", padx=10)
        
        self.output_frame = ttk.LabelFrame(main_frame, padding="15", text="Travel Itinerary")
        self.output_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        
        self.interest_vars = {}
        self.create_input_fields()
        self.create_output_display()

    def create_input_fields(self):
        header = ttk.Label(self.input_frame, text="Plan Your Journey", style='Header.TLabel')
        header.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(self.input_frame, text="Number of Countries:", style='Subheader.TLabel').grid(
            row=1, column=0, pady=8, sticky='w')
        vcmd = (self.root.register(self.validate_number), '%P')
        self.num_countries = ttk.Entry(self.input_frame, validate='key', validatecommand=vcmd)
        self.num_countries.grid(row=1, column=1, pady=8, sticky='ew')
        
        ttk.Label(self.input_frame, text="Travel Interests:", style='Subheader.TLabel').grid(
            row=2, column=0, columnspan=2, pady=(15, 5), sticky='w')
        
        interests_canvas = tk.Canvas(self.input_frame, height=150)
        interests_canvas.grid(row=3, column=0, columnspan=2, sticky='nsew')
        
        scrollbar = ttk.Scrollbar(self.input_frame, orient="vertical", command=interests_canvas.yview)
        scrollbar.grid(row=3, column=2, sticky='ns')
        
        interests_frame = ttk.Frame(interests_canvas)
        interests_canvas.create_window((0, 0), window=interests_frame, anchor='nw')
        
        for i, interest in enumerate(self.country_data.all_interests):
            var = tk.BooleanVar()
            self.interest_vars[interest] = var
            cb = ttk.Checkbutton(interests_frame, text=interest.title(), variable=var)
            cb.grid(row=i//2, column=i%2, sticky='w', padx=10, pady=2)
        
        interests_frame.bind("<Configure>", lambda e: interests_canvas.configure(
            scrollregion=interests_canvas.bbox("all")))
        
        dates_frame = ttk.LabelFrame(self.input_frame, text="Travel Dates", padding=10)
        dates_frame.grid(row=4, column=0, columnspan=2, pady=15, sticky='ew')
        
        ttk.Label(dates_frame, text="Start:").grid(row=0, column=0, padx=5)
        self.start_date = DateEntry(dates_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.start_date.grid(row=0, column=1, padx=5)
        
        ttk.Label(dates_frame, text="End:").grid(row=0, column=2, padx=5)
        self.end_date = DateEntry(dates_frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2)
        self.end_date.grid(row=0, column=3, padx=5)
        
        ttk.Label(self.input_frame, text="Budget (USD):", style='Subheader.TLabel').grid(
            row=5, column=0, pady=8, sticky='w')
        vcmd_budget = (self.root.register(self.validate_budget), '%P')
        self.budget = ttk.Entry(self.input_frame, validate='key', validatecommand=vcmd_budget)
        self.budget.grid(row=5, column=1, pady=8, sticky='ew')
        
        ttk.Label(self.input_frame, text="Home Country:", style='Subheader.TLabel').grid(
            row=6, column=0, pady=8, sticky='w')
        self.starting_country = ttk.Combobox(self.input_frame, 
                                           values=sorted(list(self.country_data.countries_data.keys())))
        self.starting_country.grid(row=6, column=1, pady=8, sticky='ew')
        
        generate_btn = ttk.Button(self.input_frame, text="Generate Itinerary ✈️", 
                                style='Custom.TButton', command=self.generate_itinerary)
        generate_btn.grid(row=7, column=0, columnspan=2, pady=20, sticky='ew')

    def create_output_display(self):
        self.result_text = tk.Text(self.output_frame, wrap=tk.WORD, 
                                 font=('Helvetica', 10), padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(self.output_frame, orient="vertical", 
                                command=self.result_text.yview)
        
        self.result_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.result_text.configure(yscrollcommand=scrollbar.set)
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(0, weight=1)
        
        welcome_msg = """
        🌍 Welcome to Global Tour Planner!
        
        Create your perfect travel itinerary by:
        1. Setting your travel parameters
        2. Selecting your interests
        3. Choosing dates and budget
        4. Clicking 'Generate Itinerary'
        
        Your personalized travel plan will appear here.
        """
        self.result_text.insert("1.0", welcome_msg)

    def validate_number(self, value):
        if value == "":
            return True
        try:
            num = int(value)
            return num > 0 and num <= 10
        except ValueError:
            return False

    def validate_budget(self, value):
        if value == "":
            return True
        try:
            num = float(value)
            return num >= 0
        except ValueError:
            return False

    def get_selected_interests(self) -> Set[str]:
        return {interest for interest, var in self.interest_vars.items() if var.get()}

    def calculate_minimum_trip_cost(self, selected_countries: List[str], home_country: str) -> float:
        min_total_cost = 0
        min_days_per_country = 2
        
        for country in selected_countries:
            country_data = self.country_data.countries_data[country]
            min_total_cost += country_data["avg_travel_cost"]
            min_total_cost += country_data["avg_accommodation_cost"] * min_days_per_country
        
        if selected_countries:
            last_country = selected_countries[-1]
            min_total_cost += self.country_data.countries_data[last_country]["avg_travel_cost"]
        
        return min_total_cost

    def suggest_alternative_plan(self, budget: float, selected_countries: List[str], 
                               home_country: str, selected_interests: Set[str]) -> Tuple[List[str], str]:
        countries_with_costs = []
        
        for country in selected_countries:
            country_data = self.country_data.countries_data[country]
            min_cost = (country_data["avg_travel_cost"] + 
                       (country_data["avg_accommodation_cost"] * 2))
            interest_match = len(set(country_data["interests"]) & selected_interests)
            
            countries_with_costs.append({
                'country': country,
                'min_cost': min_cost,
                'cost_per_interest': min_cost / interest_match if interest_match else float('inf'),
                'interest_match': interest_match
            })
        
        countries_with_costs.sort(key=lambda x: x['cost_per_interest'])
        
        remaining_budget = budget
        feasible_countries = []
        message = "Alternative plan suggestions:\n\n"
        
        for country_data in countries_with_costs:
            if remaining_budget >= country_data['min_cost']:
                feasible_countries.append(country_data['country'])
                remaining_budget -= country_data['min_cost']
            else:
                break
        
        if not feasible_countries:
            message += "⚠️ Your budget is too low for any of the selected countries.\n"
            message += "Consider:\n"
            message += "1. Increasing your budget\n"
            message += "2. Looking for cheaper destinations\n"
            message += "3. Planning a shorter trip\n"
        else:
            excluded_countries = set(selected_countries) - set(feasible_countries)
            message += f"✓ You can visit {len(feasible_countries)} out of {len(selected_countries)} selected countries.\n\n"
            message += "Countries removed to meet budget:\n"
            for country in excluded_countries:
                country_data = self.country_data.countries_data[country]
                min_cost = (country_data["avg_travel_cost"] + 
                           (country_data["avg_accommodation_cost"] * 2))
                message += f"• {country} (minimum cost: ${min_cost:,})\n"
            
            message += "\nSuggestions to include more countries:\n"
            message += "1. Reduce stay duration in each country\n"
            message += "2. Look for budget accommodation options\n"
            message += "3. Travel during off-peak seasons\n"
            message += f"4. Additional budget needed for all countries: ${self.calculate_minimum_trip_cost(selected_countries, home_country) - budget:,.2f}\n"
        
        return feasible_countries, message

    def select_countries(self, interests: Set[str], num_countries: int, 
                    home_country: str, budget: float) -> List[str]:
        """Select countries based on interests and strict budget adherence"""
        country_scores = {}
        for country, data in self.country_data.countries_data.items():
            if country != home_country:
                matching_interests = len(set(data["interests"]) & interests)
                if matching_interests > 0:
                    min_cost = data["avg_travel_cost"] + (data["avg_accommodation_cost"] * 2)  
                    country_scores[country] = {
                        'score': matching_interests,
                        'min_cost': min_cost,
                        'cost_per_interest': min_cost / matching_interests
                    }
        
        working_budget = budget * 0.9
        
        max_return_cost = max(self.country_data.countries_data[c]["avg_travel_cost"] 
                             for c in self.country_data.countries_data)
        
        working_budget -= max_return_cost
        
        sorted_countries = sorted(
            country_scores.items(),
            key=lambda x: (-x[1]['score'], x[1]['cost_per_interest'])
        )
        
        selected = []
        total_cost = 0
        
        for country, data in sorted_countries:
            if len(selected) >= num_countries - 1:
                break
                
            new_total = total_cost + data['min_cost']
            
            if new_total <= working_budget:
                selected.append(country)
                total_cost = new_total
            
        return selected

    def generate_itinerary(self):
        try:
            num_countries = int(self.num_countries.get())
            selected_interests = self.get_selected_interests()
            budget = float(self.budget.get())
            home_country = self.starting_country.get()
            
            if not selected_interests or not home_country:
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            selected_countries = self.select_countries(
                selected_interests, 
                num_countries, 
                home_country,
                budget
            )
            
            if not selected_countries:
                messagebox.showwarning(
                    "Budget Constraint",
                    "Your budget is too low to visit any countries.\n\n" +
                    "Please either:\n" +
                    "1. Increase your budget\n" +
                    "2. Consider alternative destinations\n" +
                    "3. Plan a shorter trip"
                )
                return
            
            route = self.optimizer.solve_tsp(selected_countries, home_country)
            start_date = datetime.strptime(self.start_date.get(), '%m/%d/%y')
            end_date = datetime.strptime(self.end_date.get(), '%m/%d/%y')
            total_days = (end_date - start_date).days + 1
            
            days_distribution = self.optimizer.distribute_days(total_days, route, selected_interests)
            
            total_cost = self.calculate_total_cost(route, days_distribution)
            
            if total_cost > budget:
                while total_cost > budget and len(selected_countries) > 1:
                    selected_countries.pop()
                    route = self.optimizer.solve_tsp(selected_countries, home_country)
                    days_distribution = self.optimizer.distribute_days(total_days, route, selected_interests)
                    total_cost = self.calculate_total_cost(route, days_distribution)
            
            self.display_itinerary(route, days_distribution, start_date, budget, home_country)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def calculate_total_cost(self, route: List[str], 
                            days_distribution: Dict[str, int]) -> float:
        """Calculate total cost of the itinerary"""
        total_cost = 0
        
        for country in route[1:-1]:
            country_data = self.country_data.countries_data[country]
            days = days_distribution[country]
            travel_cost = country_data["avg_travel_cost"]
            accommodation_cost = country_data["avg_accommodation_cost"] * days
            total_cost += travel_cost + accommodation_cost
        
        last_country = route[-2]
        last_country_data = self.country_data.countries_data[last_country]
        total_cost += last_country_data["avg_travel_cost"]
        
        return total_cost

    def display_itinerary(self, route: List[str], days_distribution: Dict[str, int], 
                     start_date: datetime, budget: float, home_country: str):
        """Display the generated itinerary with enhanced budget information"""
        self.result_text.delete(1.0, tk.END)
        
        total_cost = 0
        current_date = start_date
        
        total_days = sum(days_distribution.values())
        
        self.result_text.insert(tk.END, "=== Your Travel Itinerary ===\n\n")
        
        for i, country in enumerate(route[1:-1]):  
            days = days_distribution[country]
            end_date = current_date + timedelta(days=days-1)
            
            country_data = self.country_data.countries_data[country]
            travel_cost = country_data["avg_travel_cost"]
            accommodation_cost = country_data["avg_accommodation_cost"] * days
            
            total_cost += travel_cost + accommodation_cost
            
            self.result_text.insert(tk.END, f"📍 {country}\n")
            self.result_text.insert(tk.END, 
                f"   Dates: {current_date.strftime('%B %d')} - {end_date.strftime('%B %d')}\n")
            self.result_text.insert(tk.END, f"   Travel Cost: ${travel_cost:,}\n")
            self.result_text.insert(tk.END, f"   Accommodation: ${accommodation_cost:,}\n")
            self.result_text.insert(tk.END, f"   Duration: {days} days\n")
            self.result_text.insert(tk.END, f"   Interests: {', '.join(country_data['interests'])}\n\n")
            
            current_date = end_date + timedelta(days=1)
        
        last_country = route[-2]
        last_country_data = self.country_data.countries_data[last_country]
        last_travel_cost = last_country_data["avg_travel_cost"]
        total_cost += last_travel_cost
        
        self.result_text.insert(tk.END, f"📍 {home_country} \n")
        self.result_text.insert(tk.END, f"   Travel Cost: ${last_travel_cost:,}\n\n")
        
        self.result_text.insert(tk.END, "🗺️ Complete Route:\n")
        route_str = " ➔ ".join(route)
        self.result_text.insert(tk.END, f"{route_str}\n\n")
        
        self.result_text.insert(tk.END, "💰 Financial Summary:\n")
        daily_cost = total_cost / total_days
        self.result_text.insert(tk.END, f"Total Cost: ${total_cost:,}\n")
        self.result_text.insert(tk.END, f"Average Daily Cost: ${daily_cost:.2f}\n")
        remaining_budget = budget - total_cost
        budget_per_day = budget / total_days
        
        if remaining_budget < 0:
            self.result_text.insert(tk.END, 
                f"\n⚠️ Warning: Itinerary exceeds budget by ${abs(remaining_budget):,.2f}\n")
            self.result_text.insert(tk.END,
                "Budget Management Suggestions:\n")
            self.result_text.insert(tk.END,
                "1. Consider reducing stay duration in more expensive countries\n")
            self.result_text.insert(tk.END,
                "2. Look for alternative accommodation options\n")
            self.result_text.insert(tk.END,
                "3. Consider visiting fewer countries\n")
            self.result_text.insert(tk.END,
                f"4. Additional budget needed per day: ${abs(remaining_budget/total_days):.2f}\n")
        else:
            self.result_text.insert(tk.END, 
                f"\n✨ Remaining Budget: ${remaining_budget:,.2f}\n")
            self.result_text.insert(tk.END,
                f"Additional spending available per day: ${remaining_budget/total_days:.2f}\n")
            
        budget_utilization = (total_cost / budget) * 100
        self.result_text.insert(tk.END, f"\n📊 Budget Utilization: {budget_utilization:.1f}%\n")
        
        if 85 <= budget_utilization <= 100:
            self.result_text.insert(tk.END, "\n💡 Cost-Saving Opportunities:\n")
            self.result_text.insert(tk.END, "• Consider hostels or guesthouses in expensive destinations\n")
            self.result_text.insert(tk.END, "• Look for flight deals or alternative travel dates\n")
            self.result_text.insert(tk.END, "• Research free activities and attractions\n")
            self.result_text.insert(tk.END, "• Consider local transportation options\n")
            

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x720")  
    app = TourPlannerGUI(root)
    root.mainloop()
