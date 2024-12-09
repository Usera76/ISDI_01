from utils.demo_data_generator import DemoDataGenerator
generator = DemoDataGenerator()
pdf_path = generator.generate_sample_pdf()
print(f"PDF generado en: {pdf_path}")