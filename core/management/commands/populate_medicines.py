from django.core.management.base import BaseCommand
from core.models import Medicine, Hospital

class Command(BaseCommand):
    help = 'Populate medicine database with 100+ sample medicines'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hospital-id',
            type=int,
            help='Hospital ID to associate medicines with',
        )

    def handle(self, *args, **options):
        hospital_id = options.get('hospital_id')
        
        if hospital_id:
            try:
                hospital = Hospital.objects.get(id=hospital_id)
            except Hospital.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Hospital with ID {hospital_id} not found'))
                return
        else:
            # Get first hospital
            hospital = Hospital.objects.first()
            if not hospital:
                self.stdout.write(self.style.ERROR('No hospitals found. Please create a hospital first.'))
                return
        
        self.stdout.write(f'Populating medicines for hospital: {hospital.name}')
        
        medicines_data = [
            # Analgesics & Pain Relief
            ("Paracetamol", "Acetaminophen", "Tablet", "500mg", "Cipla", 150, 10.50, "Fever and pain relief"),
            ("Ibuprofen", "Ibuprofen", "Tablet", "400mg", "Pfizer", 200, 15.00, "Anti-inflammatory and pain relief"),
            ("Aspirin", "Acetylsalicylic Acid", "Tablet", "325mg", "Bayer", 180, 12.00, "Pain relief and blood thinner"),
            ("Diclofenac", "Diclofenac Sodium", "Tablet", "50mg", "Novartis", 120, 18.50, "NSAID for pain and inflammation"),
            ("Tramadol", "Tramadol HCl", "Capsule", "50mg", "Ranbaxy", 80, 45.00, "Moderate to severe pain"),
            ("Codeine", "Codeine Phosphate", "Syrup", "10mg/5ml", "Pfizer", 50, 85.00, "Cough suppressant and pain"),
            
            # Antibiotics
            ("Amoxicillin", "Amoxicillin Trihydrate", "Capsule", "500mg", "GSK", 250, 25.00, "Bacterial infections"),
            ("Azithromycin", "Azithromycin Dihydrate", "Tablet", "500mg", "Pfizer", 180, 65.00, "Bacterial infections"),
            ("Ciprofloxacin", "Ciprofloxacin HCl", "Tablet", "500mg", "Bayer", 150, 55.00, "Urinary tract infections"),
            ("Metronidazole", "Metronidazole", "Tablet", "400mg", "Sanofi", 120, 30.00, "Protozoal and bacterial infections"),
            ("Doxycycline", "Doxycycline Hyclate", "Capsule", "100mg", "Pfizer", 100, 42.00, "Bacterial infections"),
            ("Cefixime", "Cefixime Trihydrate", "Tablet", "200mg", "Lupin", 140, 75.00, "Respiratory infections"),
            ("Clarithromycin", "Clarithromycin", "Tablet", "500mg", "Abbott", 90, 95.00, "Respiratory infections"),
            ("Levofloxacin", "Levofloxacin Hemihydrate", "Tablet", "500mg", "Cipla", 110, 68.00, "Bacterial infections"),
            
            # Cardiovascular
            ("Amlodipine", "Amlodipine Besylate", "Tablet", "5mg", "Pfizer", 200, 35.00, "Hypertension and angina"),
            ("Atenolol", "Atenolol", "Tablet", "50mg", "Ranbaxy", 180, 22.00, "Hypertension and heart conditions"),
            ("Metoprolol", "Metoprolol Tartrate", "Tablet", "50mg", "Cipla", 160, 28.00, "Hypertension and angina"),
            ("Losartan", "Losartan Potassium", "Tablet", "50mg", "MSD", 150, 45.00, "Hypertension"),
            ("Enalapril", "Enalapril Maleate", "Tablet", "5mg", "GSK", 140, 32.00, "Hypertension and heart failure"),
            ("Simvastatin", "Simvastatin", "Tablet", "20mg", "Merck", 200, 48.00, "High cholesterol"),
            ("Atorvastatin", "Atorvastatin Calcium", "Tablet", "10mg", "Pfizer", 250, 85.00, "High cholesterol"),
            ("Rosuvastatin", "Rosuvastatin Calcium", "Tablet", "10mg", "AstraZeneca", 180, 120.00, "High cholesterol"),
            ("Warfarin", "Warfarin Sodium", "Tablet", "5mg", "Bristol-Myers", 100, 55.00, "Blood thinner"),
            ("Clopidogrel", "Clopidogrel Bisulfate", "Tablet", "75mg", "Sanofi", 150, 125.00, "Prevent blood clots"),
            
            # Diabetes
            ("Metformin", "Metformin HCl", "Tablet", "500mg", "BMS", 300, 25.00, "Type 2 diabetes"),
            ("Glimepiride", "Glimepiride", "Tablet", "2mg", "Sanofi", 180, 45.00, "Type 2 diabetes"),
            ("Glipizide", "Glipizide", "Tablet", "5mg", "Pfizer", 160, 38.00, "Type 2 diabetes"),
            ("Insulin Glargine", "Insulin Glargine", "Injection", "100IU/ml", "Sanofi", 80, 450.00, "Long-acting insulin"),
            ("Insulin Aspart", "Insulin Aspart", "Injection", "100IU/ml", "Novo Nordisk", 60, 520.00, "Rapid-acting insulin"),
            ("Pioglitazone", "Pioglitazone HCl", "Tablet", "15mg", "Takeda", 120, 68.00, "Type 2 diabetes"),
            ("Vildagliptin", "Vildagliptin", "Tablet", "50mg", "Novartis", 100, 180.00, "Type 2 diabetes"),
            ("Sitagliptin", "Sitagliptin Phosphate", "Tablet", "100mg", "MSD", 90, 195.00, "Type 2 diabetes"),
            
            # Gastrointestinal
            ("Omeprazole", "Omeprazole", "Capsule", "20mg", "AstraZeneca", 250, 35.00, "Acid reflux and ulcers"),
            ("Pantoprazole", "Pantoprazole Sodium", "Tablet", "40mg", "Sun Pharma", 220, 42.00, "GERD and ulcers"),
            ("Ranitidine", "Ranitidine HCl", "Tablet", "150mg", "GSK", 200, 18.00, "Heartburn and acid indigestion"),
            ("Domperidone", "Domperidone", "Tablet", "10mg", "Janssen", 180, 28.00, "Nausea and vomiting"),
            ("Ondansetron", "Ondansetron HCl", "Tablet", "4mg", "GSK", 150, 55.00, "Nausea and vomiting"),
            ("Loperamide", "Loperamide HCl", "Capsule", "2mg", "Johnson & Johnson", 200, 25.00, "Diarrhea"),
            ("Bisacodyl", "Bisacodyl", "Tablet", "5mg", "Sanofi", 160, 15.00, "Constipation"),
            ("Lactulose", "Lactulose", "Syrup", "10g/15ml", "Abbott", 80, 185.00, "Constipation"),
            ("Sucralfate", "Sucralfate", "Tablet", "1g", "Ranbaxy", 120, 65.00, "Stomach ulcers"),
            
            # Respiratory
            ("Salbutamol", "Salbutamol Sulfate", "Inhaler", "100mcg", "GSK", 150, 125.00, "Asthma and COPD"),
            ("Budesonide", "Budesonide", "Inhaler", "200mcg", "AstraZeneca", 100, 245.00, "Asthma maintenance"),
            ("Montelukast", "Montelukast Sodium", "Tablet", "10mg", "MSD", 180, 95.00, "Asthma and allergies"),
            ("Levocetirizine", "Levocetirizine Dihydrochloride", "Tablet", "5mg", "GSK", 200, 42.00, "Allergies"),
            ("Cetirizine", "Cetirizine HCl", "Tablet", "10mg", "Pfizer", 250, 28.00, "Allergic rhinitis"),
            ("Loratadine", "Loratadine", "Tablet", "10mg", "Bayer", 220, 35.00, "Allergies"),
            ("Dextromethorphan", "Dextromethorphan HBr", "Syrup", "15mg/5ml", "Pfizer", 100, 65.00, "Cough suppressant"),
            ("Ambroxol", "Ambroxol HCl", "Syrup", "30mg/5ml", "Sanofi", 120, 55.00, "Mucolytic agent"),
            
            # Neurology & Psychiatry
            ("Diazepam", "Diazepam", "Tablet", "5mg", "Roche", 100, 25.00, "Anxiety and seizures"),
            ("Alprazolam", "Alprazolam", "Tablet", "0.5mg", "Pfizer", 80, 35.00, "Anxiety disorders"),
            ("Sertraline", "Sertraline HCl", "Tablet", "50mg", "Pfizer", 120, 85.00, "Depression and anxiety"),
            ("Fluoxetine", "Fluoxetine HCl", "Capsule", "20mg", "Eli Lilly", 140, 75.00, "Depression"),
            ("Amitriptyline", "Amitriptyline HCl", "Tablet", "25mg", "Merck", 130, 28.00, "Depression and neuropathic pain"),
            ("Carbamazepine", "Carbamazepine", "Tablet", "200mg", "Novartis", 100, 45.00, "Epilepsy and seizures"),
            ("Phenytoin", "Phenytoin Sodium", "Tablet", "100mg", "Pfizer", 90, 35.00, "Epilepsy"),
            ("Gabapentin", "Gabapentin", "Capsule", "300mg", "Pfizer", 150, 125.00, "Neuropathic pain and seizures"),
            ("Pregabalin", "Pregabalin", "Capsule", "75mg", "Pfizer", 120, 185.00, "Neuropathic pain and fibromyalgia"),
            ("Sumatriptan", "Sumatriptan Succinate", "Tablet", "50mg", "GSK", 80, 145.00, "Migraine headaches"),
            
            # Dermatology
            ("Hydrocortisone", "Hydrocortisone", "Ointment", "1%", "GSK", 100, 45.00, "Skin inflammation and allergies"),
            ("Betamethasone", "Betamethasone Valerate", "Cream", "0.1%", "GSK", 80, 65.00, "Skin conditions"),
            ("Clotrimazole", "Clotrimazole", "Cream", "1%", "Bayer", 120, 55.00, "Fungal skin infections"),
            ("Miconazole", "Miconazole Nitrate", "Cream", "2%", "Johnson & Johnson", 100, 48.00, "Fungal infections"),
            ("Acyclovir", "Acyclovir", "Cream", "5%", "GSK", 60, 125.00, "Herpes simplex infections"),
            ("Calamine", "Calamine", "Lotion", "8%", "P&G", 150, 35.00, "Skin irritation and itching"),
            
            # Eye & Ear
            ("Ciprofloxacin Eye", "Ciprofloxacin HCl", "Drops", "0.3%", "Alcon", 80, 85.00, "Bacterial eye infections"),
            ("Tobramycin Eye", "Tobramycin", "Drops", "0.3%", "Alcon", 70, 95.00, "Bacterial eye infections"),
            ("Chloramphenicol Eye", "Chloramphenicol", "Drops", "0.5%", "Pfizer", 90, 55.00, "Bacterial eye infections"),
            ("Prednisolone Eye", "Prednisolone Acetate", "Drops", "1%", "Allergan", 60, 125.00, "Eye inflammation"),
            ("Tropicamide", "Tropicamide", "Drops", "1%", "Alcon", 50, 75.00, "Eye examination dilation"),
            ("Ofloxacin Ear", "Ofloxacin", "Drops", "0.3%", "Ranbaxy", 70, 68.00, "Bacterial ear infections"),
            
            # Vitamins & Supplements
            ("Vitamin D3", "Cholecalciferol", "Capsule", "60,000 IU", "Sun Pharma", 200, 45.00, "Vitamin D deficiency"),
            ("Vitamin B Complex", "B-Complex Vitamins", "Tablet", "-", "Ranbaxy", 250, 25.00, "Vitamin B deficiency"),
            ("Vitamin C", "Ascorbic Acid", "Tablet", "500mg", "P&G", 300, 18.00, "Immune support"),
            ("Calcium Carbonate", "Calcium Carbonate", "Tablet", "500mg", "Pfizer", 250, 35.00, "Calcium supplementation"),
            ("Iron Folic Acid", "Ferrous Sulfate + Folic Acid", "Tablet", "-", "Sanofi", 200, 28.00, "Anemia prevention"),
            ("Multivitamin", "Multivitamins", "Tablet", "-", "Ranbaxy", 300, 42.00, "General wellness"),
            
            # Others
            ("Prednisone", "Prednisone", "Tablet", "5mg", "Pfizer", 150, 35.00, "Anti-inflammatory"),
            ("Methylprednisolone", "Methylprednisolone", "Tablet", "4mg", "Pfizer", 120, 55.00, "Severe inflammation"),
            ("Allopurinol", "Allopurinol", "Tablet", "100mg", "GSK", 100, 45.00, "Gout"),
            ("Colchicine", "Colchicine", "Tablet", "0.5mg", "Takeda", 80, 95.00, "Gout attacks"),
            ("Methotrexate", "Methotrexate", "Tablet", "2.5mg", "Pfizer", 60, 125.00, "Rheumatoid arthritis and cancer"),
            ("Hydroxychloroquine", "Hydroxychloroquine Sulfate", "Tablet", "200mg", "Sanofi", 90, 85.00, "Malaria and autoimmune diseases"),
            ("Levothyroxine", "Levothyroxine Sodium", "Tablet", "50mcg", "Abbott", 200, 45.00, "Hypothyroidism"),
            ("Carbimazole", "Carbimazole", "Tablet", "5mg", "Abbott", 100, 55.00, "Hyperthyroidism"),
            ("Finasteride", "Finasteride", "Tablet", "1mg", "Merck", 90, 125.00, "Hair loss and prostate"),
            ("Sildenafil", "Sildenafil Citrate", "Tablet", "50mg", "Pfizer", 80, 485.00, "Erectile dysfunction"),
            ("Tadalafil", "Tadalafil", "Tablet", "10mg", "Lilly", 70, 525.00, "Erectile dysfunction"),
            ("Orlistat", "Orlistat", "Capsule", "120mg", "Roche", 100, 185.00, "Weight management"),
            ("Nitroglycerin", "Nitroglycerin", "Tablet", "0.5mg", "Pfizer", 120, 65.00, "Angina pectoris"),
            ("Isosorbide Dinitrate", "Isosorbide Dinitrate", "Tablet", "10mg", "Ranbaxy", 100, 55.00, "Angina prevention"),
            ("Digoxin", "Digoxin", "Tablet", "0.25mg", "GSK", 80, 45.00, "Heart failure"),
            ("Furosemide", "Furosemide", "Tablet", "40mg", "Sanofi", 200, 15.00, "Diuretic for edema"),
            ("Spironolactone", "Spironolactone", "Tablet", "25mg", "Pfizer", 150, 28.00, "Diuretic and heart failure"),
            ("Hydrochlorothiazide", "Hydrochlorothiazide", "Tablet", "12.5mg", "Merck", 180, 18.00, "Diuretic and hypertension"),
            ("Tamsulosin", "Tamsulosin HCl", "Capsule", "0.4mg", "Boehringer", 120, 125.00, "Enlarged prostate"),
            ("Dutasteride", "Dutasteride", "Capsule", "0.5mg", "GSK", 80, 185.00, "Enlarged prostate"),
        ]
        
        count = 0
        for med_data in medicines_data:
            name, generic, med_type, strength, manufacturer, stock, price, description = med_data
            
            medicine, created = Medicine.objects.get_or_create(
                hospital=hospital,
                name=name,
                defaults={
                    'generic_name': generic,
                    'medicine_type': med_type,
                    'manufacturer': manufacturer,
                    'stock_quantity': stock,
                    'reorder_level': max(10, stock // 10),
                    'unit_price': price,
                    'description': description,
                    'dosage_instructions': f"Take as directed by physician. {strength}",
                    'is_available': True
                }
            )
            
            if created:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} medicines'))
        self.stdout.write(self.style.SUCCESS(f'Total medicines in database: {Medicine.objects.filter(hospital=hospital).count()}'))